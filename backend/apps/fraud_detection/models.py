from django.conf import settings
from django.db import models

from apps.accounts.models import User
from apps.donations.models import FoodDonation


class FraudAlert(models.Model):
    class AlertSeverity(models.TextChoices):
        LOW = 'LOW', 'Low'
        MEDIUM = 'MEDIUM', 'Medium'
        HIGH = 'HIGH', 'High'
        CRITICAL = 'CRITICAL', 'Critical'

    class ReviewOutcome(models.TextChoices):
        NO_ACTION = 'NO_ACTION', 'No action required'
        FALSE_POSITIVE = 'FALSE_POSITIVE', 'False positive'
        POLICY_VIOLATION = 'POLICY_VIOLATION', 'Policy violation'
        ESCALATED = 'ESCALATED', 'Escalated for further review'

    class AlertStatus(models.TextChoices):
        OPEN = 'OPEN', 'Open'
        REVIEWING = 'REVIEWING', 'Reviewing'
        RESOLVED = 'RESOLVED', 'Resolved'

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fraud_alerts',
    )
    donation = models.ForeignKey(FoodDonation, on_delete=models.SET_NULL, null=True, blank=True, related_name='fraud_alerts')
    alert_type = models.CharField(max_length=80)
    severity = models.CharField(max_length=20, choices=AlertSeverity.choices, default=AlertSeverity.MEDIUM)
    risk_score = models.PositiveSmallIntegerField(default=0)
    reason = models.TextField()
    reasons = models.JSONField(default=list, blank=True)
    deduplication_key = models.CharField(max_length=64)
    detection_method = models.CharField(max_length=40, default='RULE_BASED')
    rule_version = models.CharField(max_length=40, default='fraud-rules-v1')
    occurrence_count = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=AlertStatus.choices, default=AlertStatus.OPEN)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_fraud_alerts',
    )
    review_outcome = models.CharField(max_length=30, choices=ReviewOutcome.choices, blank=True, default='')
    review_note = models.TextField(blank=True, default='')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    last_seen_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fraud_detection_fraud_alert'
        ordering = ['-risk_score', '-last_seen_at']
        constraints = [
            models.CheckConstraint(check=models.Q(risk_score__gte=0, risk_score__lte=100), name='fraud_alert_score_range'),
            models.UniqueConstraint(
                fields=['deduplication_key'],
                condition=models.Q(status__in=['OPEN', 'REVIEWING']),
                name='unique_unresolved_fraud_alert_issue',
            ),
        ]

    @property
    def risk_level(self):
        return self.severity

    def __str__(self):
        return f'{self.alert_type} ({self.severity})'


class AuditLog(models.Model):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
    )
    entity_type = models.CharField(max_length=80)
    entity_id = models.BigIntegerField(default=0)
    action = models.CharField(max_length=50)
    message = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'fraud_detection_audit_log'
        indexes = [models.Index(fields=['entity_type', 'entity_id', 'created_at'])]

    def __str__(self):
        return f'{self.action} on {self.entity_type}'
