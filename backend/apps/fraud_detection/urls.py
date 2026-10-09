from django.urls import path

from .views import FraudAlertDetailView, FraudAlertListView, FraudAlertReviewView

urlpatterns = [
	path('alerts/', FraudAlertListView.as_view(), name='fraud-alert-list'),
	path('alerts/<int:alert_id>/', FraudAlertDetailView.as_view(), name='fraud-alert-detail'),
	path('alerts/<int:alert_id>/review/', FraudAlertReviewView.as_view(), name='fraud-alert-review'),
]
