import logging

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework import filters, status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.accounts.permissions import IsVerifiedNGO

from .models import DonationRequest, DonationStatusHistory, FoodCategory, FoodDonation
from .permissions import IsDonationOwner, IsDonor
from .serializers import (
    DonationRequestCreateSerializer,
    DonationRequestSerializer,
    DonationStatusHistorySerializer,
    FoodCategorySerializer,
    FoodDonationSerializer,
)
from .services import decide_donation_request, mark_expired_if_needed, transition_donation_status

logger = logging.getLogger(__name__)


def _evaluate_fraud_safely(donation, *, event):
    # Fraud signals are for authorized human review; scoring never blocks a
    # donation operation or changes the user's access/eligibility.
    try:
        from apps.fraud_detection.services import evaluate_donation_risk

        evaluate_donation_risk(donation, event=event)
    except Exception:
        logger.exception('Fraud risk evaluation failed for donation %s.', donation.pk)


class DonationRequestCreateView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedNGO]

    def post(self, request, donation_id):
        donation = get_object_or_404(FoodDonation, pk=donation_id)
        if donation.status != FoodDonation.DonationStatus.AVAILABLE or donation.expiry_time <= timezone.now():
            return Response({'detail': 'Only unexpired available donations can be requested.'}, status=status.HTTP_409_CONFLICT)
        serializer = DonationRequestCreateSerializer(data=request.data, context={'donation': donation})
        serializer.is_valid(raise_exception=True)
        try:
            with transaction.atomic():
                donation = FoodDonation.objects.select_for_update().get(pk=donation_id)
                if donation.status != FoodDonation.DonationStatus.AVAILABLE or donation.expiry_time <= timezone.now():
                    return Response({'detail': 'This donation is no longer available.'}, status=status.HTTP_409_CONFLICT)
                donation_request = DonationRequest.objects.create(
                    donation=donation,
                    ngo=request.user,
                    requested_quantity=serializer.validated_data['requested_quantity'],
                    message=serializer.validated_data.get('message', ''),
                )
        except IntegrityError:
            return Response({'detail': 'Your organization already has a request for this donation.'}, status=status.HTTP_409_CONFLICT)
        from apps.notifications.services import create_notification

        create_notification(
            recipient=donation.donor,
            title='New NGO donation request',
            message=f'{request.user.ngo_profile.organization_name} requested {donation.food_name}.',
            event_code='DONATION_REQUESTED',
            notification_type='INFO',
            donation=donation,
            action_url='/donations/my',
        )
        return Response(DonationRequestSerializer(donation_request).data, status=status.HTTP_201_CREATED)


class DonationRequestListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role == User.Role.NGO:
            queryset = DonationRequest.objects.filter(ngo=request.user)
        elif request.user.role == User.Role.DONOR:
            queryset = DonationRequest.objects.filter(donation__donor=request.user)
        else:
            raise PermissionDenied('Donor or NGO access is required.')
        request_status = request.query_params.get('status')
        if request_status:
            if request_status not in DonationRequest.RequestStatus.values:
                return Response({'status': 'Unsupported donation request status.'}, status=status.HTTP_400_BAD_REQUEST)
            queryset = queryset.filter(status=request_status)
        queryset = queryset.select_related('ngo__ngo_profile', 'donation__donor', 'donation__category').order_by('-created_at')
        return Response(DonationRequestSerializer(queryset[:100], many=True).data)


class DonationRequestDecisionView(APIView):
    permission_classes = [IsAuthenticated, IsDonor]
    accept_request = False

    def post(self, request, request_id):
        try:
            donation_request = decide_donation_request(request_id, request.user, accept=self.accept_request)
        except DjangoValidationError as exc:
            detail = exc.message_dict if hasattr(exc, 'message_dict') else {'detail': str(exc)}
            return Response(detail, status=status.HTTP_409_CONFLICT)
        return Response(DonationRequestSerializer(donation_request).data)


class AcceptDonationRequestView(DonationRequestDecisionView):
    accept_request = True


class RejectDonationRequestView(DonationRequestDecisionView):
    accept_request = False


class NGOAcceptedDonationsView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedNGO]

    def get(self, request):
        queryset = FoodDonation.objects.filter(accepted_ngo=request.user).select_related('donor', 'category').order_by('-updated_at')
        page_number = request.query_params.get('page', '1')
        try:
            page_number = max(1, int(page_number))
        except ValueError:
            return Response({'page': 'Page must be a positive integer.'}, status=status.HTTP_400_BAD_REQUEST)
        page_size = 12
        start = (page_number - 1) * page_size
        return Response({
            'count': queryset.count(),
            'page': page_number,
            'results': FoodDonationSerializer(queryset[start:start + page_size], many=True).data,
        })


class DonationViewSet(viewsets.ModelViewSet):
    queryset = FoodDonation.objects.select_related('donor', 'category').prefetch_related('status_history__changed_by')
    serializer_class = FoodDonationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['food_name', 'description', 'pickup_address', 'category__name']
    ordering_fields = ['created_at', 'expiry_time', 'status', 'food_name']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'my_donations':
            return queryset.filter(donor=self.request.user).order_by('-created_at')

        query_status = self.request.query_params.get('status')
        category_id = self.request.query_params.get('category')
        search = self.request.query_params.get('search')

        if self.action == 'list':
            queryset = queryset.filter(status=FoodDonation.DonationStatus.AVAILABLE, expiry_time__gt=timezone.now())
        elif query_status:
            queryset = queryset.filter(status=query_status)

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        if search:
            queryset = queryset.filter(
                food_name__icontains=search,
            ) | queryset.filter(description__icontains=search)

        return queryset.order_by('-created_at')

    def get_permissions(self):
        if self.action in {'create', 'my_donations'}:
            return [IsAuthenticated(), IsDonor()]
        if self.action in {'update', 'partial_update', 'cancel'}:
            return [IsAuthenticated(), IsDonor(), IsDonationOwner()]
        return [IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        donation = serializer.save()
        donation = mark_expired_if_needed(donation)
        _evaluate_fraud_safely(donation, event='SUBMISSION')
        from apps.notifications.services import create_notification

        create_notification(
            recipient=request.user,
            title='Donation created',
            message=f'{donation.food_name} was added to your donation list.',
            event_code='DONATION_CREATED',
            notification_type='SUCCESS',
            donation=donation,
            action_url=f'/donations/{donation.pk}',
        )
        return Response(self.get_serializer(donation).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        donation = self.get_object()
        self.check_object_permissions(request, donation)
        serializer = self.get_serializer(donation, data=request.data, partial=partial, context={'request': request})
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            donation = serializer.save()
            donation = mark_expired_if_needed(donation)

        _evaluate_fraud_safely(donation, event='UPDATE')

        return Response(self.get_serializer(donation).data)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='my')
    def my_donations(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='categories')
    def categories(self, request, *args, **kwargs):
        queryset = FoodCategory.objects.all().order_by('name')
        serializer = FoodCategorySerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, *args, **kwargs):
        donation = self.get_object()
        self.check_object_permissions(request, donation)
        try:
            donation = transition_donation_status(
                donation,
                FoodDonation.DonationStatus.CANCELLED,
                actor=request.user,
                note='Cancelled by donor.',
            )
        except DjangoValidationError as exc:
            return Response(exc.message_dict if hasattr(exc, 'message_dict') else {'status': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        _evaluate_fraud_safely(donation, event='CANCELLATION')
        return Response(self.get_serializer(donation).data)

    @action(detail=True, methods=['get'], url_path='status-history')
    def status_history(self, request, *args, **kwargs):
        donation = self.get_object()
        histories = DonationStatusHistory.objects.filter(donation=donation).select_related('changed_by')
        serializer = DonationStatusHistorySerializer(histories, many=True)
        return Response(serializer.data)
