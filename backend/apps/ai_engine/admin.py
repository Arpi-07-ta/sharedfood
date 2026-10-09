from django.contrib import admin

from .models import AIRecommendation, FoodWastePrediction


@admin.register(FoodWastePrediction)
class FoodWastePredictionAdmin(admin.ModelAdmin):
    list_display = ('donation', 'predicted_waste_kg', 'risk_label', 'risk_probability', 'model_version', 'is_prototype', 'created_at')
    list_filter = ('model_version', 'risk_label', 'is_prototype')
    search_fields = ('donation__food_name',)


@admin.register(AIRecommendation)
class AIRecommendationAdmin(admin.ModelAdmin):
    list_display = ('donation', 'recommendation_type', 'score', 'urgency_level', 'created_at')
    list_filter = ('recommendation_type', 'urgency_level')
    search_fields = ('donation__food_name',)
