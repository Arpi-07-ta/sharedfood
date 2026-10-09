from rest_framework.permissions import BasePermission

from .models import User


class IsDonor(BasePermission):
    message = 'Donor access is required.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == User.Role.DONOR)


class IsVerifiedNGO(BasePermission):
    message = 'Verified NGO access is required.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.role != User.Role.NGO:
            return False
        ngo_profile = getattr(request.user, 'ngo_profile', None)
        verification = getattr(request.user, 'ngo_verification', None)
        return bool(
            request.user.is_active
            and ngo_profile
            and ngo_profile.is_verified
            and verification
            and verification.status == 'APPROVED'
        )


class IsVolunteer(BasePermission):
    message = 'Volunteer access is required.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == User.Role.VOLUNTEER)


class IsActiveVolunteer(BasePermission):
    message = 'Active volunteer access is required.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated or request.user.role != User.Role.VOLUNTEER or not request.user.is_active:
            return False
        profile = getattr(request.user, 'volunteer_profile', None)
        return bool(profile and profile.is_active)


class IsAdmin(BasePermission):
    message = 'Administrator access is required.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == User.Role.ADMIN)
