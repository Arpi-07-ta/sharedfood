from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdmin

from .models import AuditLog, FraudAlert
from .serializers import FraudAlertReviewSerializer, FraudAlertSerializer


class FraudAlertListView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        queryset = FraudAlert.objects.select_related('actor', 'donation', 'reviewed_by')
        alert_status = request.query_params.get('status')
        risk_level = request.query_params.get('risk_level')
        search = request.query_params.get('search', '').strip()
        if alert_status:
            if alert_status not in FraudAlert.AlertStatus.values:
                raise ValidationError({'status': 'Unsupported fraud alert status.'})
            queryset = queryset.filter(status=alert_status)
        if risk_level:
            if risk_level not in FraudAlert.AlertSeverity.values:
                raise ValidationError({'risk_level': 'Unsupported risk level.'})
            queryset = queryset.filter(severity=risk_level)
        if search:
            queryset = queryset.filter(reason__icontains=search) | queryset.filter(actor__username__icontains=search) | queryset.filter(donation__food_name__icontains=search)
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(queryset.order_by('-risk_score', '-last_seen_at'), request)
        return paginator.get_paginated_response(FraudAlertSerializer(page, many=True).data)


class FraudAlertDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, alert_id):
        alert = FraudAlert.objects.select_related('actor', 'donation', 'reviewed_by').filter(pk=alert_id).first()
        if alert is None:
            return Response({'detail': 'Fraud alert not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(FraudAlertSerializer(alert).data)


class FraudAlertReviewView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, alert_id):
        serializer = FraudAlertReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            alert = FraudAlert.objects.select_for_update().filter(pk=alert_id).first()
            if alert is None:
                return Response({'detail': 'Fraud alert not found.'}, status=status.HTTP_404_NOT_FOUND)
            if alert.status == FraudAlert.AlertStatus.RESOLVED:
                return Response({'detail': 'This fraud alert has already been reviewed.'}, status=status.HTTP_409_CONFLICT)

            outcome = serializer.validated_data['outcome']
            note = serializer.validated_data.get('note', '').strip()
            previous_status = alert.status
            alert.status = (
                FraudAlert.AlertStatus.REVIEWING
                if outcome == FraudAlert.ReviewOutcome.ESCALATED
                else FraudAlert.AlertStatus.RESOLVED
            )
            alert.review_outcome = outcome
            alert.review_note = note
            alert.reviewed_by = request.user
            alert.reviewed_at = timezone.now()
            alert.save(update_fields=[
                'status', 'review_outcome', 'review_note', 'reviewed_by', 'reviewed_at', 'updated_at'
            ])
            AuditLog.objects.create(
                actor=request.user,
                entity_type='FraudAlert',
                entity_id=alert.pk,
                action='REVIEWED',
                message=f'{previous_status} -> {alert.status}; outcome={outcome}; note={note}',
            )
        return Response(FraudAlertSerializer(alert).data)
