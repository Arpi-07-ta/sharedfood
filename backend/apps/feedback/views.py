from django.db import transaction
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.accounts.permissions import IsAdmin, IsVerifiedNGO
from apps.donations.models import FoodDonation
from apps.matching.models import NGORecommendation
from apps.donations.models import DonationMatch
from apps.tracking.models import Pickup

from .models import Complaint, Feedback
from .serializers import (
    ComplaintCreateSerializer,
    ComplaintReviewSerializer,
    ComplaintSerializer,
    NGOFeedbackSerializer,
)


class NGOFeedbackView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedNGO]

    def get(self, request):
        entries = Feedback.objects.filter(user=request.user).select_related('donation', 'receiver').order_by('-created_at')
        return Response(NGOFeedbackSerializer(entries, many=True).data)

    def post(self, request):
        serializer = NGOFeedbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        donation = serializer.validated_data['donation']
        if donation.status != FoodDonation.DonationStatus.COMPLETED or donation.accepted_ngo_id != request.user.pk:
            raise PermissionDenied('Feedback can only be submitted for food received by this NGO.')
        accepted_recommendation = NGORecommendation.objects.filter(
            donation=donation,
            ngo=request.user,
            status=NGORecommendation.Status.ACCEPTED,
        ).exists()
        accepted_request = DonationMatch.objects.filter(
            donation=donation,
            request__ngo=request.user,
            status=DonationMatch.MatchStatus.ACCEPTED,
        ).exists()
        if not (accepted_recommendation or accepted_request):
            raise PermissionDenied('This donation is not associated with an accepted NGO transaction.')
        if Feedback.objects.filter(user=request.user, donation=donation).exists():
            return Response({'donation': 'Feedback already exists for this completed donation.'}, status=status.HTTP_409_CONFLICT)
        entry = serializer.save(
            user=request.user,
            receiver=donation.donor,
            category='DONATION_RECEIPT',
        )
        from apps.notifications.services import create_notification

        create_notification(
            recipient=donation.donor,
            title='New donation feedback',
            message=f'{request.user.ngo_profile.organization_name} left feedback for {donation.food_name}.',
            event_code='FEEDBACK_RECEIVED',
            notification_type='INFO',
            donation=donation,
            action_url=f'/donations/{donation.pk}',
        )
        return Response(NGOFeedbackSerializer(entry).data, status=status.HTTP_201_CREATED)


class MyReceivedRatingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        aggregate = Feedback.objects.filter(receiver=request.user).aggregate(count=Count('id'), average_rating=Avg('rating'))
        return Response({
            'rating_count': aggregate['count'],
            'average_rating': round(aggregate['average_rating'], 2) if aggregate['average_rating'] is not None else None,
        })


class ComplaintCollectionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        complaints = Complaint.objects.filter(user=request.user).select_related('donation', 'reviewed_by').order_by('-created_at')
        return Response(ComplaintSerializer(complaints[:100], many=True).data)

    def post(self, request):
        serializer = ComplaintCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        donation = serializer.validated_data.get('donation')
        if donation and not self._may_complain_about_donation(request.user, donation):
            raise PermissionDenied('You must be involved in the donation transaction to submit a complaint.')
        complaint = serializer.save(user=request.user)
        from apps.notifications.services import notify_admins

        notify_admins(
            title='New complaint submitted',
            message='A new complaint is available for authorized admin review.',
            event_code='COMPLAINT_SUBMITTED',
            notification_type='WARNING',
            donation=donation,
            action_url='/admin/complaints',
        )
        return Response(ComplaintSerializer(complaint).data, status=status.HTTP_201_CREATED)

    @staticmethod
    def _may_complain_about_donation(user, donation):
        if user.role == User.Role.ADMIN:
            return True
        if user.role == User.Role.DONOR:
            return donation.donor_id == user.pk
        if user.role == User.Role.NGO:
            return donation.accepted_ngo_id == user.pk
        if user.role == User.Role.VOLUNTEER:
            return Pickup.objects.filter(donation=donation, assigned_volunteer=user).exists()
        return False


class AdminComplaintListView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        queryset = Complaint.objects.select_related('user', 'donation', 'reviewed_by')
        complaint_status = request.query_params.get('status')
        if complaint_status:
            if complaint_status not in Complaint.ComplaintStatus.values:
                return Response({'status': 'Unsupported complaint status.'}, status=status.HTTP_400_BAD_REQUEST)
            queryset = queryset.filter(status=complaint_status)
        page = max(1, int(request.query_params.get('page', 1)))
        page_size = 20
        start = (page - 1) * page_size
        return Response({
            'count': queryset.count(),
            'page': page,
            'results': ComplaintSerializer(queryset.order_by('-created_at')[start:start + page_size], many=True).data,
        })


class AdminComplaintReviewView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, complaint_id):
        serializer = ComplaintReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            complaint = get_object_or_404(Complaint.objects.select_for_update(), pk=complaint_id)
            if complaint.status == Complaint.ComplaintStatus.RESOLVED:
                return Response({'detail': 'Resolved complaints cannot be changed.'}, status=status.HTTP_409_CONFLICT)
            complaint.status = serializer.validated_data['status']
            complaint.review_note = serializer.validated_data.get('note', '').strip()
            complaint.reviewed_by = request.user
            complaint.reviewed_at = timezone.now()
            complaint.save(update_fields=['status', 'review_note', 'reviewed_by', 'reviewed_at', 'updated_at'])
            from apps.notifications.services import create_notification

            create_notification(
                recipient=complaint.user,
                title='Complaint status updated',
                message=f'Your complaint “{complaint.title}” is now {complaint.status.lower()}.',
                event_code='COMPLAINT_STATUS_UPDATED',
                notification_type='INFO',
                donation=complaint.donation,
                action_url='/complaints',
            )
        return Response(ComplaintSerializer(complaint).data)
