from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.donations.models import FoodCategory, FoodDonation


class AIEngineEndpointTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='donor-ai',
            email='donor-ai@example.com',
            password='StrongPass123!',
            role=User.Role.DONOR,
        )
        self.category = FoodCategory.objects.create(name='Produce', slug='produce')
        self.donation = FoodDonation.objects.create(
            donor=self.user,
            food_name='Fresh vegetables',
            category=self.category,
            quantity=8,
            unit='kg',
            preparation_time=None,
            expiry_time='2099-12-31T12:00:00Z',
            storage_condition=FoodDonation.StorageCondition.REFRIGERATED,
            pickup_address='123 Main St',
        )
        self.client.force_authenticate(user=self.user)

    def test_predict_wastage_success(self):
        url = reverse('predict-wastage')
        payload = {
            'food_category': 'Produce',
            'quantity': 8.5,
            'preparation_time_hours': 1.5,
            'remaining_shelf_life_hours': 18,
            'storage_condition': 'REFRIGERATED',
            'demand': 65,
            'historical_wastage_rate': 12,
            'donation_id': self.donation.id,
        }

        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('risk_label', response.data)
        self.assertIn('risk_probability', response.data)
        self.assertIn('model_status', response.data)

    def test_predict_wastage_rejects_invalid_quantity(self):
        url = reverse('predict-wastage')
        payload = {
            'food_category': 'Produce',
            'quantity': 0,
            'preparation_time_hours': 1,
            'remaining_shelf_life_hours': 12,
            'storage_condition': 'REFRIGERATED',
            'demand': 50,
            'historical_wastage_rate': 20,
        }

        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_calculate_urgency_success(self):
        url = reverse('calculate-urgency')
        payload = {
            'food_category': 'Produce',
            'quantity': 4,
            'remaining_shelf_life_hours': 8,
            'storage_condition': 'AMBIENT',
            'demand': 55,
        }

        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('urgency_score', response.data)
        self.assertIn('urgency_level', response.data)
        self.assertGreaterEqual(response.data['urgency_score'], 0)
        self.assertLessEqual(response.data['urgency_score'], 100)
