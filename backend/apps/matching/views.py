from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from apps.accounts.models import User
from apps.donations.models import FoodDonation

from .models import NGORecommendation, NGOMatchingProfile
from .serializers import NGORecommendationSerializer, NGOMatchingProfileSerializer
from .services import MatchingError, accept_recommendation, decline_recommendation, generate_recommendations

ACTIVE_MATCH_STATUSES = [NGORecommendation.Status.RECOMMENDED, NGORecommendation.Status.ACCEPTED]


def _serialize_paginated(queryset, request):
    paginator = PageNumberPagination()
    page = paginator.paginate_queryset(queryset, request)
    serializer = NGORecommendationSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


class MatchingProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_ngo(self, request):
        if request.user.role != User.Role.NGO or not request.user.is_active:
            raise PermissionDenied('Active NGO access is required.')
        return request.user

    def get(self, request):
        ngo = self._get_ngo(request)
        profile, _ = NGOMatchingProfile.objects.get_or_create(ngo=ngo)
        return Response(NGOMatchingProfileSerializer(profile).data)

    def patch(self, request):
        ngo = self._get_ngo(request)
        profile, _ = NGOMatchingProfile.objects.get_or_create(ngo=ngo)
        serializer = NGOMatchingProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class GenerateMatchesView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, donation_id):
        if request.user.role != User.Role.DONOR:
            raise PermissionDenied('Only donors can generate recommendations for their donations.')
        donation = get_object_or_404(FoodDonation, pk=donation_id, donor=request.user)
        try:
            limit = int(request.query_params.get('limit', 10))
            if not 1 <= limit <= 50:
                raise ValueError
        except (TypeError, ValueError):
            return Response({'detail': 'limit must be an integer from 1 to 50.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            recommendations = generate_recommendations(donation.pk, limit=limit)
        except MatchingError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        payload = NGORecommendationSerializer(recommendations, many=True).data
        return Response({
            'score_type': 'weighted_ranking_score',
            'count': len(payload),
            'results': payload,
        }, status=status.HTTP_200_OK)


class DonationMatchesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, donation_id):
        donation = get_object_or_404(FoodDonation, pk=donation_id)
        if request.user.role == User.Role.DONOR:
            if donation.donor_id != request.user.pk:
                raise PermissionDenied('You can only view matches for your own donations.')
            queryset = NGORecommendation.objects.filter(donation=donation, status__in=ACTIVE_MATCH_STATUSES)
        elif request.user.role == User.Role.NGO:
            queryset = NGORecommendation.objects.filter(
                donation=donation,
                ngo=request.user,
                status__in=ACTIVE_MATCH_STATUSES,
            )
        else:
            raise PermissionDenied('Donor or NGO access is required.')
        queryset = queryset.select_related('donation__category', 'ngo__ngo_profile').order_by('-match_score', 'ngo_id')
        return _serialize_paginated(queryset, request)


class MyMatchesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = NGORecommendation.objects.filter(status__in=ACTIVE_MATCH_STATUSES)
        if request.user.role == User.Role.DONOR:
            queryset = queryset.filter(donation__donor=request.user)
        elif request.user.role == User.Role.NGO:
            queryset = queryset.filter(ngo=request.user)
        else:
            raise PermissionDenied('Donor or NGO access is required.')
        queryset = queryset.select_related('donation__category', 'ngo__ngo_profile').order_by('-match_score', '-created_at')
        return _serialize_paginated(queryset, request)


class RecommendationDecisionView(APIView):
    permission_classes = [IsAuthenticated]
    decision = None

    def post(self, request, recommendation_id):
        if request.user.role != User.Role.NGO:
            raise PermissionDenied('Only NGOs can respond to a recommendation.')
        try:
            if self.decision == 'accept':
                recommendation = accept_recommendation(recommendation_id, request.user)
            else:
                recommendation = decline_recommendation(recommendation_id, request.user)
        except MatchingError as exc:
            response_status = status.HTTP_409_CONFLICT if self.decision == 'accept' else status.HTTP_400_BAD_REQUEST
            return Response({'detail': str(exc)}, status=response_status)
        return Response(NGORecommendationSerializer(recommendation).data)


class AcceptRecommendationView(RecommendationDecisionView):
    decision = 'accept'


class DeclineRecommendationView(RecommendationDecisionView):
    decision = 'decline'
