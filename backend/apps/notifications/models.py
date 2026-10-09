from django.conf import settings
from django.db import models

from apps.donations.models import FoodDonation


class Notification(models.Model):
    class NotificationType(models.TextChoices):
        INFO = 'INFO', 'Info'
        SUCCESS = 'SUCCESS', 'Success'
        WARNING = 'WARNING', 'Warning'
        ALERT = 'ALERT', 'Alert'

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        limit_choices_to={'is_active': True},
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    event_code = models.CharField(max_length=60, default='GENERAL')
    action_url = models.CharField(max_length=500, blank=True, default='')
    notification_type = models.CharField(max_length=20, choices=NotificationType.choices, default=NotificationType.INFO)
    is_read = models.BooleanField(default=False)
    related_donation = models.ForeignKey(
        FoodDonation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications_notification'
        indexes = [models.Index(fields=['recipient', 'is_read', 'created_at'])]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} -> {self.recipient}'
