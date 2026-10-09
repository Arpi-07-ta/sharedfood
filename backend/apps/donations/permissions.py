from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsDonor(BasePermission):
    message = 'Only donors can access donation management endpoints.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request.user, 'role', None) == 'DONOR')


class IsDonationOwner(BasePermission):
    message = 'You can only manage your own donations.'

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and obj.donor_id == request.user.id)
