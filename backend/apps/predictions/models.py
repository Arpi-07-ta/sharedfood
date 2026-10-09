from django.db import models


class PredictionResult(models.Model):
    """Placeholder model for AI-generated waste and donation predictions."""

    model_name = models.CharField(max_length=255)
    prediction_value = models.FloatField(default=0.0)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.model_name} @ {self.created_at}'
