from django.conf import settings
from django.db import models

from apps.accounts.models import User
from apps.donations.models import FoodDonation
from apps.accounts.storage import PrivateUploadStorage


class Beneficiary(models.Model):
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=30, blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')
    state = models.CharField(max_length=100, blank=True, default='')
    address = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tracking_beneficiary'

    def __str__(self):
        return self.name


class Pickup(models.Model):
    class PickupStatus(models.TextChoices):
        SCHEDULED = 'SCHEDULED', 'Scheduled'
        ACCEPTED = 'ACCEPTED', 'Accepted by volunteer'
        IN_TRANSIT = 'IN_TRANSIT', 'In transit'
        PICKED_UP = 'PICKED_UP', 'Picked up'
        DELIVERED = 'DELIVERED', 'Delivered'
        CANCELLED = 'CANCELLED', 'Cancelled'

    donation = models.ForeignKey(FoodDonation, on_delete=models.CASCADE, related_name='pickups')
    ngo = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='ngo_pickups',
        limit_choices_to={'role': User.Role.NGO},
    )
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.PROTECT, related_name='pickups')
    assigned_volunteer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_pickups',
        limit_choices_to={'role': User.Role.VOLUNTEER},
    )
    status = models.CharField(max_length=20, choices=PickupStatus.choices, default=PickupStatus.SCHEDULED)
    pickup_window_start = models.DateTimeField()
    pickup_window_end = models.DateTimeField()
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    received_at = models.DateTimeField(null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'tracking_pickup'
        constraints = [
            models.CheckConstraint(check=models.Q(pickup_window_end__gt=models.F('pickup_window_start')), name='pickup_window_valid'),
            models.UniqueConstraint(
                fields=['donation'],
                condition=~models.Q(status='CANCELLED'),
                name='unique_active_pickup_per_donation',
            ),
        ]

    def __str__(self):
        return f'Pickup for {self.donation} ({self.status})'


class DeliveryLog(models.Model):
    pickup = models.ForeignKey(Pickup, on_delete=models.CASCADE, related_name='delivery_logs')
    delivered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='delivery_logs',
    )
    delivered_at = models.DateTimeField(auto_now_add=True)
    condition = models.CharField(max_length=50, default='GOOD')
    comment = models.TextField(blank=True, default='')
    proof_file = models.FileField(upload_to='delivery-proofs/', storage=PrivateUploadStorage(), blank=True, null=True)

    class Meta:
        db_table = 'tracking_delivery_log'
        constraints = [
            models.UniqueConstraint(fields=['pickup'], name='unique_delivery_log_per_pickup'),
        ]

    def __str__(self):
        return f'Delivery for {self.pickup}'


class PickupStatusHistory(models.Model):
    pickup = models.ForeignKey(Pickup, on_delete=models.CASCADE, related_name='status_history')
    previous_status = models.CharField(max_length=20, choices=Pickup.PickupStatus.choices, blank=True, default='')
    new_status = models.CharField(max_length=20, choices=Pickup.PickupStatus.choices)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pickup_status_changes',
    )
    note = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tracking_pickup_status_history'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.pickup_id}: {self.previous_status} -> {self.new_status}'
