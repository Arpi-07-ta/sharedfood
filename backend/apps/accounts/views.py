from django.db import transaction
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import NGOProfile, NGOVerification, User, VolunteerProfile
from .permissions import IsAdmin, IsDonor, IsVerifiedNGO, IsVolunteer
from .serializers import (
    FoodShareTokenObtainPairSerializer,
    NGOProfileSerializer,
    NGOVerificationReviewSerializer,
    NGOVerificationStatusSerializer,
    NGOVerificationSubmissionSerializer,
    ProfileUpdateSerializer,
    RegisterSerializer,
    UserSerializer,
    VolunteerProfileSerializer,
)
from apps.matching.models import NGOMatchingProfile


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({'status': 'ok', 'module': 'accounts'})


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = TokenRefreshView().get_serializer_class() if False else None
        from rest_framework_simplejwt.tokens import RefreshToken

        token = RefreshToken.for_user(user)
        user_data = UserSerializer(user).data
        return Response(
            {
                'user': user_data,
                'email': user_data['email'],
                'access': str(token.access_token),
                'refresh': str(token),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    serializer_class = FoodShareTokenObtainPairSerializer


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)


class NGOProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def _profile(self, request):
        if request.user.role != User.Role.NGO or not request.user.is_active:
            raise PermissionDenied('Active NGO access is required.')
        profile, _ = NGOProfile.objects.get_or_create(
            user=request.user,
            defaults={'organization_name': request.user.get_full_name() or request.user.username},
        )
        return profile

    def get(self, request):
        return Response(NGOProfileSerializer(self._profile(request)).data)

    def patch(self, request):
        profile = self._profile(request)
        serializer = NGOProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            profile = serializer.save()
            matching_profile, _ = NGOMatchingProfile.objects.get_or_create(ngo=request.user)
            matching_profile.latitude = profile.latitude
            matching_profile.longitude = profile.longitude
            matching_profile.save(update_fields=['latitude', 'longitude', 'updated_at'])
        return Response(serializer.data)


class VolunteerProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def _profile(self, request):
        if request.user.role != User.Role.VOLUNTEER or not request.user.is_active:
            raise PermissionDenied('Active volunteer access is required.')
        profile, _ = VolunteerProfile.objects.get_or_create(user=request.user)
        return profile

    def get(self, request):
        return Response(VolunteerProfileSerializer(self._profile(request)).data)

    def patch(self, request):
        profile = self._profile(request)
        serializer = VolunteerProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class NGOVerificationView(APIView):
    permission_classes = [IsAuthenticated]

    def _verification(self, request):
        if request.user.role != User.Role.NGO or not request.user.is_active:
            raise PermissionDenied('Active NGO access is required.')
        verification, _ = NGOVerification.objects.get_or_create(
            ngo=request.user,
            defaults={
                'organization_name': getattr(request.user, 'ngo_profile', None).organization_name
                if hasattr(request.user, 'ngo_profile') else request.user.get_full_name(),
                'registration_number': getattr(request.user, 'ngo_profile', None).registration_number
                if hasattr(request.user, 'ngo_profile') else '',
            },
        )
        return verification

    def get(self, request):
        verification = self._verification(request)
        return Response(NGOVerificationStatusSerializer(verification).data)

    def post(self, request):
        verification = self._verification(request)
        if verification.status == NGOVerification.Status.APPROVED:
            return Response({'detail': 'An approved NGO cannot replace its verification submission.'}, status=status.HTTP_409_CONFLICT)
        serializer = NGOVerificationSubmissionSerializer(verification, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            verification = serializer.save(
                status=NGOVerification.Status.PENDING,
                verified_by=None,
                review_note='',
                reviewed_at=None,
            )
            NGOProfile.objects.filter(user=request.user).update(is_verified=False)
            from apps.notifications.services import notify_admins

            notify_admins(
                title='NGO verification submitted',
                message=f'{verification.organization_name} submitted verification documents for review.',
                event_code='NGO_VERIFICATION_SUBMITTED',
                notification_type='INFO',
                action_url='/admin/ngo-verifications',
            )
        return Response(NGOVerificationStatusSerializer(verification).data, status=status.HTTP_200_OK)


class AdminNGOVerificationListView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        queryset = NGOVerification.objects.select_related('ngo', 'verified_by').order_by('created_at')
        status_filter = request.query_params.get('status', NGOVerification.Status.PENDING)
        if status_filter not in NGOVerification.Status.values:
            return Response({'status': 'Unsupported verification status.'}, status=status.HTTP_400_BAD_REQUEST)
        queryset = queryset.filter(status=status_filter)
        page_number = request.query_params.get('page', '1')
        try:
            page_number = max(1, int(page_number))
        except ValueError:
            return Response({'page': 'Page must be a positive integer.'}, status=status.HTTP_400_BAD_REQUEST)
        page_size = 20
        start = (page_number - 1) * page_size
        rows = queryset[start:start + page_size]
        return Response({
            'count': queryset.count(),
            'page': page_number,
            'results': [
                {
                    **NGOVerificationStatusSerializer(item).data,
                    'ngo_id': item.ngo_id,
                    'ngo_email': item.ngo.email,
                    'phone_number': item.ngo.phone_number,
                    'document_endpoint': f'/api/auth/admin/ngo-verifications/{item.pk}/document/',
                }
                for item in rows
            ],
        })


class AdminNGOVerificationReviewView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, verification_id):
        serializer = NGOVerificationReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            verification = get_object_or_404(
                NGOVerification.objects.select_for_update().select_related('ngo'),
                pk=verification_id,
            )
            decision = serializer.validated_data['status']
            verification.status = decision
            verification.review_note = serializer.validated_data.get('note', '').strip()
            verification.verified_by = request.user
            verification.reviewed_at = timezone.now()
            verification.save(update_fields=['status', 'review_note', 'verified_by', 'reviewed_at', 'updated_at'])
            NGOProfile.objects.filter(user=verification.ngo).update(
                is_verified=decision == NGOVerification.Status.APPROVED,
            )
            from apps.notifications.services import create_notification

            create_notification(
                recipient=verification.ngo,
                title=f'NGO verification {decision.lower()}',
                message=verification.review_note or f'Your verification status is now {decision.lower()}.',
                event_code='NGO_VERIFICATION_REVIEWED',
                notification_type='SUCCESS' if decision == NGOVerification.Status.APPROVED else 'WARNING',
                action_url='/dashboard/ngo',
            )
        return Response({
            **NGOVerificationStatusSerializer(verification).data,
            'ngo_id': verification.ngo_id,
            'ngo_email': verification.ngo.email,
        })


class NGOVerificationDocumentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, verification_id):
        verification = get_object_or_404(NGOVerification, pk=verification_id)
        if request.user.role != User.Role.ADMIN and verification.ngo_id != request.user.pk:
            raise PermissionDenied('You cannot access another organization\'s verification document.')
        if not verification.document:
            return Response({'detail': 'No uploaded verification document.'}, status=status.HTTP_404_NOT_FOUND)
        return FileResponse(
            verification.document.open('rb'),
            as_attachment=True,
            filename=verification.document.name.rsplit('/', 1)[-1],
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsDonor])
def donor_only_view(request):
    return Response({'detail': 'Donor access granted.'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsVerifiedNGO])
def verified_ngo_only_view(request):
    return Response({'detail': 'Verified NGO access granted.'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsVolunteer])
def volunteer_only_view(request):
    return Response({'detail': 'Volunteer access granted.'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_only_view(request):
    return Response({'detail': 'Admin access granted.'}, status=status.HTTP_200_OK)
