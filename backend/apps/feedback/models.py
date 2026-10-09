from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.donations.models import FoodDonation


class Feedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='feedback_entries')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='feedback_received')
    donation = models.ForeignKey(FoodDonation, on_delete=models.SET_NULL, null=True, blank=True, related_name='feedback')
    category = models.CharField(max_length=50, default='GENERAL')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'feedback_feedback'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'donation'],
                condition=models.Q(donation__isnull=False),
                name='unique_feedback_per_user_donation',
            ),
        ]

    def __str__(self):
        return f'{self.user} feedback ({self.rating}/5)'


class Complaint(models.Model):
    class ComplaintStatus(models.TextChoices):
        OPEN = 'OPEN', 'Open'
        REVIEWING = 'REVIEWING', 'Reviewing'
        RESOLVED = 'RESOLVED', 'Resolved'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='complaints')
    donation = models.ForeignKey(FoodDonation, on_delete=models.SET_NULL, null=True, blank=True, related_name='complaints')
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=ComplaintStatus.choices, default='OPEN')
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_complaints',
    )
    review_note = models.TextField(blank=True, default='')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'feedback_complaint'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} ({self.status})'
