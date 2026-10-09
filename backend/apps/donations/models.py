from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from apps.accounts.models import User


class FoodCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'donations_food_category'
        ordering = ['name']

    def __str__(self):
        return self.name


class FoodDonation(models.Model):
    class DonationStatus(models.TextChoices):
        AVAILABLE = 'AVAILABLE', 'Available'
        MATCHED = 'MATCHED', 'Matched'
        ACCEPTED = 'ACCEPTED', 'Accepted'
        PICKUP_SCHEDULED = 'PICKUP_SCHEDULED', 'Pickup scheduled'
        PICKED_UP = 'PICKED_UP', 'Picked up'
        DELIVERED = 'DELIVERED', 'Delivered'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'
        EXPIRED = 'EXPIRED', 'Expired'
        REJECTED = 'REJECTED', 'Rejected'

    class StorageCondition(models.TextChoices):
        AMBIENT = 'AMBIENT', 'Ambient'
        REFRIGERATED = 'REFRIGERATED', 'Refrigerated'
        FROZEN = 'FROZEN', 'Frozen'
        ROOM_TEMPERATURE = 'ROOM_TEMPERATURE', 'Room temperature'

    donor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='food_donations',
        limit_choices_to={'role': User.Role.DONOR},
    )
    accepted_ngo = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='accepted_donations',
        limit_choices_to={'role': User.Role.NGO},
    )
    food_name = models.CharField(max_length=255)
    category = models.ForeignKey(FoodCategory, on_delete=models.PROTECT, related_name='donations')
    description = models.TextField(blank=True, default='')
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    unit = models.CharField(max_length=30, default='kg')
    preparation_time = models.DateTimeField(blank=True, null=True)
    expiry_time = models.DateTimeField()
    storage_condition = models.CharField(
        max_length=30,
        choices=StorageCondition.choices,
        default=StorageCondition.AMBIENT,
    )
    pickup_address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    image = models.ImageField(upload_to='donations/', blank=True, null=True)
    status = models.CharField(
        max_length=32,
        choices=DonationStatus.choices,
        default=DonationStatus.AVAILABLE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'donations_food_donation'
        indexes = [
            models.Index(fields=['status', 'expiry_time']),
            models.Index(fields=['donor', 'status']),
        ]
        constraints = [
            models.CheckConstraint(check=models.Q(quantity__gt=0), name='food_donation_quantity_positive'),
            models.CheckConstraint(check=~models.Q(food_name=''), name='food_donation_name_required'),
            models.CheckConstraint(check=~models.Q(pickup_address=''), name='food_donation_pickup_address_required'),
        ]

    @property
    def is_expired(self):
        return self.expiry_time <= timezone.now()

    @property
    def can_be_edited(self):
        return self.status in {
            self.DonationStatus.AVAILABLE,
            self.DonationStatus.MATCHED,
            self.DonationStatus.ACCEPTED,
            self.DonationStatus.PICKUP_SCHEDULED,
        }

    def __str__(self):
        return f'{self.food_name} ({self.status})'


class DonationStatusHistory(models.Model):
    donation = models.ForeignKey(FoodDonation, on_delete=models.CASCADE, related_name='status_history')
    previous_status = models.CharField(max_length=32, choices=FoodDonation.DonationStatus.choices, blank=True, default='')
    new_status = models.CharField(max_length=32, choices=FoodDonation.DonationStatus.choices)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='donation_status_changes')
    note = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'donations_status_history'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.donation} {self.previous_status} -> {self.new_status}'


class DonationRequest(models.Model):
    class RequestStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        ACCEPTED = 'ACCEPTED', 'Accepted'
        REJECTED = 'REJECTED', 'Rejected'
        CANCELLED = 'CANCELLED', 'Cancelled'

    donation = models.ForeignKey(FoodDonation, on_delete=models.CASCADE, related_name='requests')
    ngo = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='donation_requests',
        limit_choices_to={'role': User.Role.NGO},
    )
    requested_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    message = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=RequestStatus.choices, default=RequestStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'donations_donation_request'
        indexes = [models.Index(fields=['status', 'created_at'])]
        constraints = [
            models.CheckConstraint(check=models.Q(requested_quantity__gt=0), name='donation_request_quantity_positive'),
            models.UniqueConstraint(fields=['donation', 'ngo'], name='unique_request_per_donation_and_ngo'),
        ]

    def __str__(self):
        return f'{self.ngo} request for {self.donation}'


class DonationMatch(models.Model):
    class MatchStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        ACCEPTED = 'ACCEPTED', 'Accepted'
        REJECTED = 'REJECTED', 'Rejected'
        CANCELLED = 'CANCELLED', 'Cancelled'

    donation = models.ForeignKey(FoodDonation, on_delete=models.CASCADE, related_name='matches')
    request = models.ForeignKey(DonationRequest, on_delete=models.CASCADE, related_name='matches')
    matched_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='matches',
    )
    status = models.CharField(max_length=20, choices=MatchStatus.choices, default=MatchStatus.PENDING)
    match_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    note = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'donations_donation_match'
        constraints = [
            models.UniqueConstraint(fields=['donation', 'request'], name='unique_donation_match_per_request'),
            models.CheckConstraint(check=models.Q(match_score__gte=0), name='match_score_non_negative'),
            models.UniqueConstraint(
                fields=['donation'],
                condition=models.Q(status='ACCEPTED'),
                name='unique_accepted_donation_match',
            ),
        ]

    def __str__(self):
        return f'Match for {self.donation} -> {self.request}'
