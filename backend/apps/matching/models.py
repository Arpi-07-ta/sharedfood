from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.accounts.models import User
from apps.donations.models import DonationRequest, FoodCategory, FoodDonation


class NGOMatchingProfile(models.Model):
    """Matching inputs maintained by an NGO; reliability is admin-managed."""

    ngo = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='matching_profile',
        limit_choices_to={'role': User.Role.NGO},
    )
    accepted_categories = models.ManyToManyField(FoodCategory, related_name='matching_ngos', blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    capacity_kg = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))])
    current_demand_score = models.PositiveSmallIntegerField(default=50, validators=[MinValueValidator(0), MaxValueValidator(100)])
    reliability_score = models.PositiveSmallIntegerField(default=50, validators=[MinValueValidator(0), MaxValueValidator(100)])
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'matching_ngo_profile'
        constraints = [
            models.CheckConstraint(check=models.Q(latitude__isnull=True) | models.Q(latitude__gte=-90, latitude__lte=90), name='ngo_match_latitude_range'),
            models.CheckConstraint(check=models.Q(longitude__isnull=True) | models.Q(longitude__gte=-180, longitude__lte=180), name='ngo_match_longitude_range'),
            models.CheckConstraint(check=models.Q(current_demand_score__lte=100), name='ngo_match_demand_score_range'),
            models.CheckConstraint(check=models.Q(reliability_score__lte=100), name='ngo_match_reliability_score_range'),
        ]

    def __str__(self):
        return f'Matching profile for {self.ngo}'


class NGORecommendation(models.Model):
    class Status(models.TextChoices):
        RECOMMENDED = 'RECOMMENDED', 'Recommended'
        ACCEPTED = 'ACCEPTED', 'Accepted'
        DECLINED = 'DECLINED', 'Declined'
        SUPERSEDED = 'SUPERSEDED', 'Superseded'

    donation = models.ForeignKey(FoodDonation, on_delete=models.CASCADE, related_name='ngo_recommendations')
    ngo = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ngo_recommendations', limit_choices_to={'role': User.Role.NGO})
    match_score = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))])
    factor_scores = models.JSONField(default=dict)
    factor_weights = models.JSONField(default=dict)
    distance_km = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    explanation = models.JSONField(default=list)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RECOMMENDED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'matching_ngo_recommendation'
        ordering = ['-match_score', '-created_at']
        constraints = [
            models.CheckConstraint(check=models.Q(match_score__gte=0, match_score__lte=100), name='ngo_match_score_range'),
            models.UniqueConstraint(
                fields=['donation', 'ngo'],
                condition=models.Q(status__in=['RECOMMENDED', 'ACCEPTED']),
                name='unique_active_ngo_match_per_donation',
            ),
            models.UniqueConstraint(
                fields=['donation'],
                condition=models.Q(status='ACCEPTED'),
                name='unique_accepted_ngo_per_donation',
            ),
        ]

    def __str__(self):
        return f'{self.donation} -> {self.ngo} ({self.match_score})'


class MatchCandidate(models.Model):
    donation = models.ForeignKey(FoodDonation, on_delete=models.CASCADE, related_name='match_candidates')
    request = models.ForeignKey(DonationRequest, on_delete=models.CASCADE, related_name='match_candidates')
    compatibility_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(Decimal('0.00'))],
    )
    reason = models.TextField(blank=True, default='')
    matched_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='match_candidates',
        limit_choices_to={'role': User.Role.ADMIN},
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'matching_match_candidate'
        constraints = [
            models.UniqueConstraint(fields=['donation', 'request'], name='unique_match_candidate_for_donation_request'),
            models.CheckConstraint(check=models.Q(compatibility_score__gte=0), name='match_candidate_score_non_negative'),
        ]

    def __str__(self):
        return f'{self.donation} vs {self.request} ({self.compatibility_score})'


class MatchAudit(models.Model):
    donation = models.ForeignKey(FoodDonation, on_delete=models.CASCADE, related_name='match_audits')
    request = models.ForeignKey(DonationRequest, on_delete=models.CASCADE, related_name='match_audits')
    decision = models.CharField(max_length=20, default='PENDING')
    notes = models.TextField(blank=True, default='')
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='match_reviews',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'matching_match_audit'

    def __str__(self):
        return f'{self.donation} match audit - {self.decision}'
