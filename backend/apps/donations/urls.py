from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AcceptDonationRequestView,
    DonationRequestCreateView,
    DonationRequestListView,
    DonationViewSet,
    NGOAcceptedDonationsView,
    RejectDonationRequestView,
)

router = DefaultRouter()
router.register(r'', DonationViewSet, basename='donation')

urlpatterns = [
    path('accepted/', NGOAcceptedDonationsView.as_view(), name='ngo-accepted-donations'),
    path('requests/my/', DonationRequestListView.as_view(), name='donation-requests-my'),
    path('requests/<int:request_id>/accept/', AcceptDonationRequestView.as_view(), name='donation-request-accept'),
    path('requests/<int:request_id>/reject/', RejectDonationRequestView.as_view(), name='donation-request-reject'),
    path('<int:donation_id>/requests/', DonationRequestCreateView.as_view(), name='donation-request-create'),
    path('', include(router.urls)),
]
