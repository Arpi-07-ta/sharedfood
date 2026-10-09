from django.urls import path

from .views import CalculateUrgencyView, PredictWastageView

urlpatterns = [
    path('predict-wastage/', PredictWastageView.as_view(), name='predict-wastage'),
    path('calculate-urgency/', CalculateUrgencyView.as_view(), name='calculate-urgency'),
]
