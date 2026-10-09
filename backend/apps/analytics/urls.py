from django.urls import path

from .views import NGOAnalyticsView

urlpatterns = [
	path('ngo/summary/', NGOAnalyticsView.as_view(), name='ngo-analytics-summary'),
]
