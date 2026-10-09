from django.urls import path

from .views import (
	AcceptRecommendationView,
	DeclineRecommendationView,
	DonationMatchesView,
	GenerateMatchesView,
	MatchingProfileView,
	MyMatchesView,
)

urlpatterns = [
	path('profile/', MatchingProfileView.as_view(), name='matching-profile'),
	path('my/', MyMatchesView.as_view(), name='my-matches'),
	path('donations/<int:donation_id>/generate/', GenerateMatchesView.as_view(), name='generate-matches'),
	path('donations/<int:donation_id>/matches/', DonationMatchesView.as_view(), name='donation-matches'),
	path('matches/<int:recommendation_id>/accept/', AcceptRecommendationView.as_view(), name='accept-match'),
	path('matches/<int:recommendation_id>/decline/', DeclineRecommendationView.as_view(), name='decline-match'),
]
