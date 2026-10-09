from datetime import timedelta

from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.donations.models import DonationStatusHistory, FoodCategory, FoodDonation
from apps.feedback.models import Complaint

from .models import AuditLog, FraudAlert
from .services import evaluate_donation_risk


class FraudDetectionServiceTests(TestCase):
    def setUp(self):
        self.donor = User.objects.create_user(
            username='fraud-donor', email='fraud-donor@example.com', password='StrongPass123!', role=User.Role.DONOR
        )
        self.complainant = User.objects.create_user(
            username='complainant', email='complainant@example.com', password='StrongPass123!', role=User.Role.USER
        )
        self.category = FoodCategory.objects.create(name='Fraud Produce', slug='fraud-produce')

    def create_donation(self, **overrides):
        values = {
            'donor': self.donor,
            'food_name': 'Fresh apples',
            'category': self.category,
            'quantity': 10,
            'unit': 'kg',
            'expiry_time': timezone.now() + timedelta(days=2),
            'storage_condition': FoodDonation.StorageCondition.REFRIGERATED,
            'pickup_address': '10 Market Street',
        }
        values.update(overrides)
        return FoodDonation.objects.create(**values)

    def test_ordinary_donation_has_low_risk_and_no_alert(self):
        donation = self.create_donation()

        result = evaluate_donation_risk(donation)

        self.assertEqual(result['risk_score'], 0)
        self.assertEqual(result['risk_level'], FraudAlert.AlertSeverity.LOW)
        self.assertEqual(result['review_status'], 'NOT_FLAGGED')
        self.assertEqual(result['detection_method'], 'RULE_BASED')
        self.assertEqual(FraudAlert.objects.count(), 0)

    def test_similar_donation_creates_explained_alert(self):
        previous = self.create_donation()
        FoodDonation.objects.filter(pk=previous.pk).update(created_at=timezone.now() - timedelta(hours=1))
        current = self.create_donation(food_name='Fresh apples!!', quantity=10.5)

        result = evaluate_donation_risk(current)

        self.assertIn('SIMILAR_DONATION', [item['code'] for item in result['reasons']])
        alert = FraudAlert.objects.get(donation=current)
        self.assertEqual(alert.risk_score, 35)
        self.assertIn('similar', alert.reason.lower())
        self.assertEqual(alert.detection_method, 'RULE_BASED')

    def test_unrealistic_quantity_is_flagged_without_blocking_creation(self):
        donation = self.create_donation(quantity=650)

        result = evaluate_donation_risk(donation)

        self.assertEqual(result['risk_score'], 40)
        self.assertIn('UNREALISTIC_QUANTITY', [item['code'] for item in result['reasons']])
        self.assertTrue(FraudAlert.objects.filter(donation=donation).exists())

    def test_repeated_cancellations_and_complaints_raise_account_risk(self):
        donation = self.create_donation()
        for _ in range(3):
            DonationStatusHistory.objects.create(
                donation=donation,
                previous_status=FoodDonation.DonationStatus.AVAILABLE,
                new_status=FoodDonation.DonationStatus.CANCELLED,
            )
        for index in range(3):
            Complaint.objects.create(
                user=self.complainant,
                donation=donation,
                title=f'Issue {index}',
                description='Reported issue',
            )

        result = evaluate_donation_risk(donation)

        codes = {item['code'] for item in result['reasons']}
        self.assertIn('REPEATED_CANCELLATIONS', codes)
        self.assertIn('REPEATED_COMPLAINTS', codes)
        self.assertEqual(result['risk_level'], FraudAlert.AlertSeverity.HIGH)
        self.assertTrue(FraudAlert.objects.filter(alert_type='ACCOUNT_ACTIVITY', actor=self.donor).exists())

    @override_settings(FRAUD_FREQUENT_SUBMISSION_COUNT=2)
    def test_suspicious_submission_frequency_is_flagged(self):
        self.create_donation(food_name='Earlier apples')
        latest = self.create_donation(food_name='Latest oranges')

        result = evaluate_donation_risk(latest)

        self.assertIn('FREQUENT_SUBMISSIONS', [item['code'] for item in result['reasons']])

    def test_unresolved_alert_is_deduplicated_and_refreshed(self):
        previous = self.create_donation()
        FoodDonation.objects.filter(pk=previous.pk).update(created_at=timezone.now() - timedelta(hours=1))
        current = self.create_donation(food_name='Fresh apples!')

        evaluate_donation_risk(current)
        evaluate_donation_risk(current)

        self.assertEqual(FraudAlert.objects.filter(donation=current, status=FraudAlert.AlertStatus.OPEN).count(), 1)
        self.assertEqual(FraudAlert.objects.get(donation=current).occurrence_count, 2)


class FraudAlertAdminAPITests(APITestCase):
    def setUp(self):
        self.donor = User.objects.create_user(
            username='api-donor', email='api-donor@example.com', password='StrongPass123!', role=User.Role.DONOR
        )
        self.admin = User.objects.create_user(
            username='fraud-admin', email='fraud-admin@example.com', password='StrongPass123!', role=User.Role.ADMIN
        )
        self.category = FoodCategory.objects.create(name='API Produce', slug='api-produce')
        self.donation = FoodDonation.objects.create(
            donor=self.donor,
            food_name='Oversized donation',
            category=self.category,
            quantity=700,
            unit='kg',
            expiry_time=timezone.now() + timedelta(days=1),
            storage_condition=FoodDonation.StorageCondition.AMBIENT,
            pickup_address='Private pickup location',
        )
        evaluate_donation_risk(self.donation)
        self.alert = FraudAlert.objects.get(donation=self.donation)

    def test_alerts_are_hidden_from_donors_and_unauthenticated_callers(self):
        response = self.client.get('/api/fraud-detection/alerts/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(user=self.donor)
        response = self.client.get('/api/fraud-detection/alerts/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_donation_creation_runs_scoring_without_exposing_internal_alert(self):
        self.client.force_authenticate(user=self.donor)
        response = self.client.post('/api/donations/', {
            'food_name': 'Bulk rice',
            'category': self.category.pk,
            'quantity': '750',
            'unit': 'kg',
            'pickup_address': 'Private address',
            'expiry_time': (timezone.now() + timedelta(days=1)).isoformat(),
            'storage_condition': FoodDonation.StorageCondition.AMBIENT,
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('risk_score', response.data)
        self.assertNotIn('reasons', response.data)
        self.assertTrue(FraudAlert.objects.filter(donation_id=response.data['id']).exists())

    def test_admin_can_list_view_and_review_alert(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/fraud-detection/alerts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['risk_score'], 40)
        self.assertEqual(response.data['results'][0]['risk_level'], 'MEDIUM')

        detail = self.client.get(f'/api/fraud-detection/alerts/{self.alert.pk}/')
        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertNotIn('pickup_address', detail.data)

        reviewed = self.client.post(
            f'/api/fraud-detection/alerts/{self.alert.pk}/review/',
            {'outcome': FraudAlert.ReviewOutcome.FALSE_POSITIVE, 'note': 'Verified donation; no action needed.'},
            format='json',
        )
        self.assertEqual(reviewed.status_code, status.HTTP_200_OK)
        self.assertEqual(reviewed.data['status'], FraudAlert.AlertStatus.RESOLVED)
        self.assertEqual(reviewed.data['review_outcome'], FraudAlert.ReviewOutcome.FALSE_POSITIVE)
        self.assertEqual(reviewed.data['reviewed_by_id'], self.admin.pk)
        self.assertTrue(AuditLog.objects.filter(entity_type='FraudAlert', entity_id=self.alert.pk, action='REVIEWED').exists())

        duplicate_review = self.client.post(
            f'/api/fraud-detection/alerts/{self.alert.pk}/review/',
            {'outcome': FraudAlert.ReviewOutcome.NO_ACTION},
            format='json',
        )
        self.assertEqual(duplicate_review.status_code, status.HTTP_409_CONFLICT)

    def test_admin_review_requires_valid_outcome(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            f'/api/fraud-detection/alerts/{self.alert.pk}/review/',
            {'outcome': 'BAN_USER'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.alert.status, FraudAlert.AlertStatus.OPEN)

    def test_escalated_review_remains_in_reviewing_status(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            f'/api/fraud-detection/alerts/{self.alert.pk}/review/',
            {'outcome': FraudAlert.ReviewOutcome.ESCALATED, 'note': 'Needs a second reviewer.'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], FraudAlert.AlertStatus.REVIEWING)
        self.assertEqual(response.data['review_outcome'], FraudAlert.ReviewOutcome.ESCALATED)
