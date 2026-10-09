from django.shortcuts import get_object_or_404
from django.http import FileResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.accounts.permissions import IsActiveVolunteer, IsAdmin, IsDonor, IsVerifiedNGO
from apps.donations.models import FoodDonation

from .models import Pickup
from .serializers import PickupScheduleSerializer, PickupSerializer, PickupStatusUpdateSerializer
from .services import (
    PickupWorkflowError,
    accept_pickup,
    confirm_ngo_received,
    schedule_ngo_pickup,
    transition_pickup,
)


def _pickup_queryset():
    return Pickup.objects.select_related(
        'donation__donor', 'donation__category', 'ngo__ngo_profile', 'assigned_volunteer', 'beneficiary'
    ).prefetch_related('status_history__changed_by', 'delivery_logs')


def _serialize_list(queryset):
    return Response(PickupSerializer(queryset, many=True).data)


class VolunteerAssignmentsView(APIView):
    permission_classes = [IsAuthenticated, IsActiveVolunteer]

    def get(self, request):
        pickups = _pickup_queryset().filter(assigned_volunteer=request.user).order_by('-pickup_window_start')
        return _serialize_list(pickups)


class AvailableVolunteerPickupsView(APIView):
    permission_classes = [IsAuthenticated, IsActiveVolunteer]

    def get(self, request):
        pickups = _pickup_queryset().filter(
            assigned_volunteer__isnull=True,
            status=Pickup.PickupStatus.SCHEDULED,
            donation__status=FoodDonation.DonationStatus.PICKUP_SCHEDULED,
            donation__expiry_time__gt=timezone.now(),
        ).order_by('pickup_window_start')
        return _serialize_list(pickups)


class PickupDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pickup_id):
        pickup = get_object_or_404(_pickup_queryset(), pk=pickup_id)
        user = request.user
        allowed = (
            user.role == User.Role.ADMIN
            or (user.role == User.Role.VOLUNTEER and pickup.assigned_volunteer_id == user.pk)
            or (user.role == User.Role.NGO and pickup.ngo_id == user.pk)
            or (user.role == User.Role.DONOR and pickup.donation.donor_id == user.pk)
        )
        if not allowed:
            raise PermissionDenied('You cannot view this pickup.')
        return Response(PickupSerializer(pickup).data)


class DeliveryProofView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pickup_id):
        pickup = get_object_or_404(Pickup.objects.select_related('donation'), pk=pickup_id)
        user = request.user
        allowed = (
            user.role == User.Role.ADMIN
            or (user.role == User.Role.VOLUNTEER and pickup.assigned_volunteer_id == user.pk)
            or (user.role == User.Role.NGO and pickup.ngo_id == user.pk)
            or (user.role == User.Role.DONOR and pickup.donation.donor_id == user.pk)
        )
        if not allowed:
            raise PermissionDenied('You cannot access proof for this pickup.')
        proof = pickup.delivery_logs.order_by('-delivered_at').first()
        if not proof or not proof.proof_file:
            return Response({'detail': 'No delivery proof is attached.'}, status=status.HTTP_404_NOT_FOUND)
        return FileResponse(
            proof.proof_file.open('rb'),
            as_attachment=True,
            filename=proof.proof_file.name.rsplit('/', 1)[-1],
        )


class AcceptPickupView(APIView):
    permission_classes = [IsAuthenticated, IsActiveVolunteer]

    def post(self, request, pickup_id):
        try:
            pickup = accept_pickup(pickup_id, request.user)
        except PickupWorkflowError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_409_CONFLICT)
        return Response(PickupSerializer(pickup).data)


class PickupStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pickup_id):
        serializer = PickupStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        actor = request.user
        if actor.role == User.Role.VOLUNTEER:
            if not Pickup.objects.filter(pk=pickup_id, assigned_volunteer=actor).exists():
                raise PermissionDenied('Volunteers can update only pickups assigned to them.')
        elif actor.role != User.Role.ADMIN:
            raise PermissionDenied('Only the assigned volunteer or an administrator can update pickup status.')
        try:
            pickup = transition_pickup(
                pickup_id,
                serializer.validated_data['status'],
                actor,
                note=serializer.validated_data.get('note', ''),
                proof_file=serializer.validated_data.get('proof_file'),
            )
        except PickupWorkflowError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_409_CONFLICT)
        return Response(PickupSerializer(pickup).data)


class NGOPickupListView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedNGO]

    def get(self, request):
        pickups = _pickup_queryset().filter(ngo=request.user).order_by('-pickup_window_start')
        return _serialize_list(pickups)


class ScheduleNGOPickupView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedNGO]

    def post(self, request, donation_id):
        serializer = PickupScheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            pickup = schedule_ngo_pickup(
                donation_id,
                request.user,
                serializer.validated_data['pickup_window_start'],
                serializer.validated_data['pickup_window_end'],
                serializer.validated_data.get('notes', ''),
            )
        except PickupWorkflowError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_409_CONFLICT)
        return Response(PickupSerializer(pickup).data, status=status.HTTP_201_CREATED)


class ConfirmReceivedView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedNGO]

    def post(self, request, pickup_id):
        try:
            pickup = confirm_ngo_received(pickup_id, request.user)
        except PickupWorkflowError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_409_CONFLICT)
        return Response(PickupSerializer(pickup).data)


class DonorPickupListView(APIView):
    permission_classes = [IsAuthenticated, IsDonor]

    def get(self, request):
        pickups = _pickup_queryset().filter(donation__donor=request.user).order_by('-pickup_window_start')
        return _serialize_list(pickups)


class AdminPickupListView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        pickups = _pickup_queryset().order_by('-pickup_window_start')
        return _serialize_list(pickups)
