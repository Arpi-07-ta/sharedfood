from decimal import Decimal

from django.conf import settings
from django.db import models

from apps.accounts.models import User


class ImpactMetric(models.Model):
    report_date = models.DateField()
    ngo = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='impact_metrics',
        limit_choices_to={'role': User.Role.NGO},
    )
    meals_distributed = models.BigIntegerField(default=0)
    kilograms_rescued = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    waste_avoided_kg = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    donors_engaged = models.PositiveIntegerField(default=0)
    volunteers_engaged = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'analytics_impact_metric'
        unique_together = ('report_date', 'ngo')

    def __str__(self):
        return f'{self.report_date} impact for {self.ngo}'
