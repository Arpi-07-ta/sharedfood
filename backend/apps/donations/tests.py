from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.donations.models import FoodCategory, FoodDonation


class DonationAPITests(APITestCase):
    def setUp(self):
        self.category = FoodCategory.objects.create(name='Fresh Produce', slug='fresh-produce', description='Produce')
        self.donor = User.objects.create_user(
            username='donor-user',
            email='donor@example.com',
            password='StrongPass123!',
            role=User.Role.DONOR,
            phone_number='+123456789',
        )
        self.other_donor = User.objects.create_user(
            username='other-donor',
            email='other@example.com',
            password='StrongPass123!',
            role=User.Role.DONOR,
        )
        self.ngo = User.objects.create_user(
            username='ngo-user',
            email='ngo@example.com',
            password='StrongPass123!',
            role=User.Role.NGO,
        )

    def _make_image_file(self, name='test.png', size=(50, 50), color='green'):
        image = Image.new('RGB', size, color)
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        return SimpleUploadedFile(name, buffer.read(), content_type='image/png')

    def test_create_donation_success_for_donor(self):
        self.client.force_authenticate(user=self.donor)
        payload = {
            'food_name': 'Apples',
            'category': self.category.id,
            'description': 'Fresh apples',
            'quantity': '10',
            'unit': 'kg',
            'storage_condition': 'AMBIENT',
            'pickup_address': '123 Lake Street',
            'expiry_time': '2030-12-31T18:00:00Z',
            'preparation_time': '2026-10-09T09:00:00Z',
        }

        response = self.client.post(reverse('donation-list'), payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['donor']['id'], self.donor.id)
        self.assertEqual(response.data['status'], FoodDonation.DonationStatus.AVAILABLE)

    def test_create_donation_rejects_invalid_expiry(self):
        self.client.force_authenticate(user=self.donor)
        payload = {
            'food_name': 'Bread',
            'category': self.category.id,
            'quantity': '2',
            'pickup_address': '456 Main Rd',
            'expiry_time': '2020-01-01T12:00:00Z',
        }

        response = self.client.post(reverse('donation-list'), payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('expiry_time', response.data)

    def test_non_donor_cannot_create_donation(self):
        self.client.force_authenticate(user=self.ngo)
        payload = {
            'food_name': 'Soup',
            'category': self.category.id,
            'quantity': '1',
            'pickup_address': '200 Community St',
            'expiry_time': '2030-01-01T12:00:00Z',
        }

        response = self.client.post(reverse('donation-list'), payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_donations_filters_and_searches(self):
        self.client.force_authenticate(user=self.donor)
        FoodDonation.objects.create(
            donor=self.donor,
            food_name='Carrots',
            category=self.category,
            quantity='3',
            pickup_address='1 Street',
            expiry_time='2030-10-10T12:00:00Z',
            status=FoodDonation.DonationStatus.AVAILABLE,
        )
        FoodDonation.objects.create(
            donor=self.donor,
            food_name='Cakes',
            category=self.category,
            quantity='5',
            pickup_address='2 Street',
            expiry_time='2030-10-10T12:00:00Z',
            status=FoodDonation.DonationStatus.CANCELLED,
        )

        response = self.client.get(reverse('donation-list'), {'search': 'car', 'category': str(self.category.id)})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['food_name'], 'Carrots')

    def test_invalid_image_upload_rejected(self):
        self.client.force_authenticate(user=self.donor)
        payload = {
            'food_name': 'Bananas',
            'category': self.category.id,
            'quantity': '4',
            'pickup_address': '222 Green Avenue',
            'expiry_time': '2030-11-11T12:00:00Z',
            'image': SimpleUploadedFile('invalid.txt', b'not-an-image', content_type='text/plain'),
        }

        response = self.client.post(reverse('donation-list'), payload, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('image', response.data)

    def test_status_transition_prevents_invalid_change(self):
        donation = FoodDonation.objects.create(
            donor=self.donor,
            food_name='Salad',
            category=self.category,
            quantity='2',
            pickup_address='77 Street',
            expiry_time='2030-10-10T12:00:00Z',
            status=FoodDonation.DonationStatus.AVAILABLE,
        )
        self.client.force_authenticate(user=self.donor)

        response = self.client.patch(reverse('donation-detail', args=[donation.id]), {'status': FoodDonation.DonationStatus.PICKED_UP}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('status', response.data)

    def test_donor_can_cancel_own_donation(self):
        donation = FoodDonation.objects.create(
            donor=self.donor,
            food_name='Rice',
            category=self.category,
            quantity='1.5',
            pickup_address='44 Avenue',
            expiry_time='2030-10-10T12:00:00Z',
            status=FoodDonation.DonationStatus.AVAILABLE,
        )
        self.client.force_authenticate(user=self.donor)

        response = self.client.post(reverse('donation-cancel', args=[donation.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        donation.refresh_from_db()
        self.assertEqual(donation.status, FoodDonation.DonationStatus.CANCELLED)
