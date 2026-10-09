from datetime import timedelta
from decimal import Decimal

from django.test import override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import NGOVerification, NGOProfile, User
from apps.donations.models import FoodCategory, FoodDonation, DonationStatusHistory

from .models import NGORecommendation, NGOMatchingProfile
from .services import (
    generate_recommendations,
    haversine_distance_km,
    rank_eligible_ngos,
    weighted_match_score,
)


class MatchingServiceTests(APITestCase):
    def setUp(self):
        self.donor = User.objects.create_user(
            username='match-donor',
            email='match-donor@example.com',
            password='StrongPass123!',
            role=User.Role.DONOR,
        )
        self.ngo = User.objects.create_user(
            username='match-ngo',
            email='match-ngo@example.com',
            password='StrongPass123!',
            role=User.Role.NGO,
        )
        NGOProfile.objects.create(user=self.ngo, organization_name='Verified Pantry', is_verified=True)
        NGOVerification.objects.create(
            ngo=self.ngo,
            organization_name='Verified Pantry',
            registration_number='REG-1',
            status=NGOVerification.Status.APPROVED,
        )
        self.category = FoodCategory.objects.create(name='Produce Match', slug='produce-match')
        self.donation = FoodDonation.objects.create(
            donor=self.donor,
            food_name='Fresh apples',
            category=self.category,
            quantity=10,
            unit='kg',
            expiry_time=timezone.now() + timedelta(hours=8),
            storage_condition=FoodDonation.StorageCondition.REFRIGERATED,
            pickup_address='1 Donor Way',
            latitude=Decimal('47.606200'),
            longitude=Decimal('-122.332100'),
        )
        self.profile = NGOMatchingProfile.objects.create(
            ngo=self.ngo,
            latitude=Decimal('47.609000'),
            longitude=Decimal('-122.335000'),
            capacity_kg=Decimal('25.00'),
            current_demand_score=80,
            reliability_score=90,
        )
        self.profile.accepted_categories.add(self.category)

    def test_haversine_distance_for_same_point_and_known_pair(self):
        self.assertAlmostEqual(haversine_distance_km(47.6062, -122.3321, 47.6062, -122.3321), 0, places=6)
        self.assertGreater(haversine_distance_km(47.6062, -122.3321, 47.6090, -122.3350), 0.3)

    def test_weighted_score_uses_normalized_factor_values_and_weights(self):
        score = weighted_match_score(
            {
                'distance': 0,
                'food_compatibility': 100,
                'urgency': 100,
                'capacity': 100,
                'current_demand': 100,
                'reliability': 100,
            },
            {
                'distance': 0.30,
                'food_compatibility': 0.20,
                'urgency': 0.20,
                'capacity': 0.15,
                'current_demand': 0.10,
                'reliability': 0.05,
            },
        )
        self.assertEqual(score, Decimal('70.00'))

    def test_missing_coordinates_use_neutral_distance_score(self):
        self.donation.latitude = None
        self.donation.longitude = None
        self.donation.save(update_fields=['latitude', 'longitude'])
        self.profile.latitude = None
        self.profile.longitude = None
        self.profile.save(update_fields=['latitude', 'longitude'])

        [result] = rank_eligible_ngos(self.donation)
        self.assertIsNone(result['distance_km'])
        self.assertEqual(result['factor_scores']['distance'], 50.0)
        self.assertIn('Distance unavailable', result['explanation'][0])

    def test_capacity_excludes_ngos_that_cannot_accept_donation(self):
        self.profile.capacity_kg = Decimal('9.99')
        self.profile.save(update_fields=['capacity_kg'])
        self.assertEqual(rank_eligible_ngos(self.donation), [])

    def test_only_active_verified_ngos_with_matching_categories_are_ranked(self):
        pending = User.objects.create_user(
            username='pending-ngo', email='pending@example.com', password='StrongPass123!', role=User.Role.NGO
        )
        NGOProfile.objects.create(user=pending, organization_name='Pending Pantry', is_verified=True)
        NGOVerification.objects.create(
            ngo=pending,
            organization_name='Pending Pantry',
            registration_number='REG-P',
            status=NGOVerification.Status.PENDING,
        )
        pending_profile = NGOMatchingProfile.objects.create(ngo=pending, capacity_kg=Decimal('50'))
        pending_profile.accepted_categories.add(self.category)

        inactive = User.objects.create_user(
            username='inactive-ngo', email='inactive@example.com', password='StrongPass123!', role=User.Role.NGO, is_active=False
        )
        NGOProfile.objects.create(user=inactive, organization_name='Inactive Pantry', is_verified=True)
        NGOVerification.objects.create(
            ngo=inactive,
            organization_name='Inactive Pantry',
            registration_number='REG-I',
            status=NGOVerification.Status.APPROVED,
        )
        inactive_profile = NGOMatchingProfile.objects.create(ngo=inactive, capacity_kg=Decimal('50'))
        inactive_profile.accepted_categories.add(self.category)

        [result] = rank_eligible_ngos(self.donation)
        self.assertEqual(result['ngo'], self.ngo)

    @override_settings(MATCHING_WEIGHTS={
        'distance': 0.30,
        'food_compatibility': 0.20,
        'urgency': 0.20,
        'capacity': 0.15,
        'current_demand': 0.10,
        'reliability': 0.05,
    })
    def test_generation_is_persisted_and_refresh_does_not_duplicate_active_matches(self):
        first = generate_recommendations(self.donation.pk)
        second = generate_recommendations(self.donation.pk)
        self.assertEqual(len(first), 1)
        self.assertEqual(len(second), 1)
        self.assertEqual(
            NGORecommendation.objects.filter(
                donation=self.donation,
                ngo=self.ngo,
                status=NGORecommendation.Status.RECOMMENDED,
            ).count(),
            1,
        )
        self.assertEqual(first[0].factor_scores['food_compatibility'], 100.0)
        self.assertEqual(first[0].factor_weights['distance'], 0.30)

    def test_donor_can_generate_and_retrieve_recommendations(self):
        self.client.force_authenticate(user=self.donor)
        generate_url = f'/api/matching/donations/{self.donation.pk}/generate/'
        response = self.client.post(generate_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['score_type'], 'weighted_ranking_score')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['ngo_name'], 'Verified Pantry')
        self.assertIn('Food Compatibility:', response.data['results'][0]['explanation'][1])
        recommendation_id = response.data['results'][0]['id']

        response = self.client.get(f'/api/matching/donations/{self.donation.pk}/matches/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['id'], recommendation_id)

    def test_ngo_acceptance_transitions_donation_atomically(self):
        [recommendation] = generate_recommendations(self.donation.pk)
        self.client.force_authenticate(user=self.ngo)
        response = self.client.post(f'/api/matching/matches/{recommendation.pk}/accept/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        recommendation.refresh_from_db()
        self.donation.refresh_from_db()
        self.assertEqual(recommendation.status, NGORecommendation.Status.ACCEPTED)
        self.assertEqual(self.donation.status, FoodDonation.DonationStatus.ACCEPTED)
        self.assertEqual(
            DonationStatusHistory.objects.filter(donation=self.donation).count(),
            2,
        )

    def test_acceptance_rechecks_current_capacity(self):
        [recommendation] = generate_recommendations(self.donation.pk)
        self.profile.capacity_kg = Decimal('5.00')
        self.profile.save(update_fields=['capacity_kg'])
        self.client.force_authenticate(user=self.ngo)

        response = self.client.post(f'/api/matching/matches/{recommendation.pk}/accept/', {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.donation.refresh_from_db()
        self.assertEqual(self.donation.status, FoodDonation.DonationStatus.AVAILABLE)
