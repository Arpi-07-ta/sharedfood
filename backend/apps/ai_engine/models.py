from decimal import Decimal

from django.db import models

from apps.donations.models import FoodDonation


class FoodWastePrediction(models.Model):
    donation = models.OneToOneField(FoodDonation, on_delete=models.CASCADE, related_name='waste_prediction', null=True, blank=True)
    predicted_waste_kg = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    risk_label = models.CharField(max_length=20, default='LOW')
    risk_probability = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0.00'))
    model_version = models.CharField(max_length=80, default='foodshare-prototype-v1')
    feature_summary = models.JSONField(default=dict, blank=True)
    is_prototype = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_engine_food_waste_prediction'

    def __str__(self):
        return f'Prediction for {self.donation} - {self.predicted_waste_kg} kg'


class AIRecommendation(models.Model):
    donation = models.ForeignKey(FoodDonation, on_delete=models.CASCADE, related_name='ai_recommendations')
    recommendation_type = models.CharField(max_length=50, default='MATCH')
    score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    urgency_level = models.CharField(max_length=20, default='MEDIUM')
    explanation = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_engine_ai_recommendation'

    def __str__(self):
        return f'{self.recommendation_type} for {self.donation}'
