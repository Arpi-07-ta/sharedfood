from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.donations.models import FoodDonation
from .models import AIRecommendation, FoodWastePrediction
from .serializers import FoodWastePredictionSerializer, UrgencyCalculationSerializer
from .services import calculate_food_urgency, predict_food_waste


class PredictWastageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = FoodWastePredictionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data

        try:
            prediction = predict_food_waste(payload)
        except FileNotFoundError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as exc:  # pragma: no cover - defensive error handling
            return Response({'detail': f'Wastage prediction failed: {exc}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        donation = payload.get('donation')
        risk_probability = Decimal(str(prediction['risk_probability']))
        predicted_waste_kg = Decimal(str(prediction['predicted_waste_kg']))
        model_status = prediction.get('model_status', 'prototype')

        prediction_record = None
        with transaction.atomic():
            if donation:
                prediction_record, _ = FoodWastePrediction.objects.update_or_create(
                    donation=donation,
                    defaults={
                        'predicted_waste_kg': predicted_waste_kg,
                        'risk_label': prediction['risk_label'],
                        'risk_probability': risk_probability,
                        'model_version': prediction.get('model_version', 'prototype-random-forest-v1'),
                        'feature_summary': prediction.get('feature_summary', {}),
                        'is_prototype': model_status == 'prototype',
                    },
                )

        response = {
            'risk_label': prediction['risk_label'],
            'risk_probability': prediction['risk_probability'],
            'predicted_waste_kg': prediction['predicted_waste_kg'],
            'urgency_signal': prediction.get('urgency_signal'),
            'model_status': model_status,
            'model_version': prediction.get('model_version', 'prototype-random-forest-v1'),
            'generated_at': timezone.now().isoformat(),
            'prediction_id': prediction_record.id if prediction_record else None,
            'donation_id': donation.id if donation else None,
        }
        return Response(response, status=status.HTTP_200_OK)


class CalculateUrgencyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = UrgencyCalculationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data

        urgency = calculate_food_urgency(payload)
        donation = payload.get('donation')

        with transaction.atomic():
            if donation:
                AIRecommendation.objects.create(
                    donation=donation,
                    recommendation_type='URGENT_DONATION',
                    score=Decimal(str(urgency['urgency_score'])),
                    urgency_level=urgency['urgency_level'],
                    explanation=urgency['explanation'],
                )

        return Response(
            {
                'urgency_score': urgency['urgency_score'],
                'urgency_level': urgency['urgency_level'],
                'explanation': urgency['explanation'],
                'donation_id': donation.id if donation else None,
            },
            status=status.HTTP_200_OK,
        )
