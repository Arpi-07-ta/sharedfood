from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import NGOProfile, User


class AuthAPITests(APITestCase):
    def setUp(self):
        self.user_data = {
            'username': 'donoruser',
            'email': 'donor@example.com',
            'first_name': 'Donor',
            'last_name': 'User',
            'phone_number': '+123456789',
            'role': User.Role.DONOR,
            'password': 'StrongPass123!',
        }

    def test_registration_creates_user(self):
        response = self.client.post(reverse('auth-register'), {
            'username': self.user_data['username'],
            'email': self.user_data['email'],
            'first_name': self.user_data['first_name'],
            'last_name': self.user_data['last_name'],
            'phone_number': self.user_data['phone_number'],
            'role': self.user_data['role'],
            'password': self.user_data['password'],
            'confirm_password': self.user_data['password'],
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.data['email'], self.user_data['email'])
        self.assertNotIn('password', response.data)

    def test_registration_rejects_admin_role(self):
        response = self.client.post(reverse('auth-register'), {
            'username': 'admin-try',
            'email': 'admin-try@example.com',
            'password': 'StrongPass123!',
            'confirm_password': 'StrongPass123!',
            'role': User.Role.ADMIN,
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('role', response.data)

    def test_login_returns_tokens(self):
        User.objects.create_user(
            username='donoruser',
            email='donor@example.com',
            password='StrongPass123!',
            role=User.Role.DONOR,
            phone_number='+123456789',
        )

        response = self.client.post(reverse('token-obtain-pair'), {
            'email': 'donor@example.com',
            'password': 'StrongPass123!',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_invalid_credentials_fail(self):
        User.objects.create_user(
            username='donoruser',
            email='donor@example.com',
            password='StrongPass123!',
            role=User.Role.DONOR,
        )

        response = self.client.post(reverse('token-obtain-pair'), {
            'email': 'donor@example.com',
            'password': 'WrongPassword',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_requires_authentication(self):
        response = self.client.get(reverse('auth-profile'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_returns_authenticated_user(self):
        user = User.objects.create_user(
            username='donoruser',
            email='donor@example.com',
            password='StrongPass123!',
            role=User.Role.DONOR,
            phone_number='+123456789',
        )
        self.client.force_authenticate(user=user)

        response = self.client.get(reverse('auth-profile'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'donor@example.com')
        self.assertNotIn('password', response.data)

    def test_donor_only_route_restricts_non_donors(self):
        user = User.objects.create_user(
            username='ngo-user',
            email='ngo@example.com',
            password='StrongPass123!',
            role=User.Role.NGO,
        )
        self.client.force_authenticate(user=user)

        response = self.client.get(reverse('auth-donor-only'))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_verified_ngo_only_route_allows_verified_ngo(self):
        user = User.objects.create_user(
            username='ngo-verified',
            email='ngo-verified@example.com',
            password='StrongPass123!',
            role=User.Role.NGO,
        )
        NGOProfile.objects.create(user=user, organization_name='Community Kitchen', is_verified=True)
        self.client.force_authenticate(user=user)

        response = self.client.get(reverse('auth-verified-ngo-only'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
