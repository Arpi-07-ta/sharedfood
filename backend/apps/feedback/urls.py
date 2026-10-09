from django.urls import path

from .views import (
	AdminComplaintListView,
	AdminComplaintReviewView,
	ComplaintCollectionView,
	MyReceivedRatingsView,
	NGOFeedbackView,
)

urlpatterns = [
	path('ngo/', NGOFeedbackView.as_view(), name='ngo-feedback'),
	path('me/ratings/', MyReceivedRatingsView.as_view(), name='my-received-ratings'),
	path('complaints/', ComplaintCollectionView.as_view(), name='complaint-collection'),
	path('admin/complaints/', AdminComplaintListView.as_view(), name='admin-complaint-list'),
	path('admin/complaints/<int:complaint_id>/review/', AdminComplaintReviewView.as_view(), name='admin-complaint-review'),
]
