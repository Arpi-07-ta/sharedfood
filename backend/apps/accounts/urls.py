from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    LoginView,
    RegisterView,
    ProfileView,
    admin_only_view,
    donor_only_view,
    health_check,
    AdminNGOVerificationListView,
    AdminNGOVerificationReviewView,
    NGOProfileView,
    NGOVerificationDocumentView,
    NGOVerificationView,
    VolunteerProfileView,
    verified_ngo_only_view,
    volunteer_only_view,
)

urlpatterns = [
    path('health/', health_check, name='accounts-health'),
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('login/', LoginView.as_view(), name='token-obtain-pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('profile/', ProfileView.as_view(), name='auth-profile'),
    path('ngo/profile/', NGOProfileView.as_view(), name='ngo-profile'),
    path('ngo/verification/', NGOVerificationView.as_view(), name='ngo-verification'),
    path('volunteer/profile/', VolunteerProfileView.as_view(), name='volunteer-profile'),
    path('admin/ngo-verifications/', AdminNGOVerificationListView.as_view(), name='ngo-verification-list'),
    path('admin/ngo-verifications/<int:verification_id>/review/', AdminNGOVerificationReviewView.as_view(), name='ngo-verification-review'),
    path('admin/ngo-verifications/<int:verification_id>/document/', NGOVerificationDocumentView.as_view(), name='ngo-verification-document'),
    path('role/donor-only/', donor_only_view, name='auth-donor-only'),
    path('role/verified-ngo-only/', verified_ngo_only_view, name='auth-verified-ngo-only'),
    path('role/volunteer-only/', volunteer_only_view, name='auth-volunteer-only'),
    path('role/admin-only/', admin_only_view, name='auth-admin-only'),
]
