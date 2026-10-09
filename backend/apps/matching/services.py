from __future__ import annotations

from decimal import Decimal
from math import asin, cos, radians, sin, sqrt

from django.conf import settings
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from apps.accounts.models import NGOVerification, NGOProfile, User
from apps.donations.models import DonationStatusHistory, FoodDonation
from apps.donations.services import transition_donation_status

from .models import NGORecommendation, NGOMatchingProfile

DEFAULT_WEIGHTS = {
    'distance': 0.30,
    'food_compatibility': 0.20,
    'urgency': 0.20,
    'capacity': 0.15,
    'current_demand': 0.10,
    'reliability': 0.05,
}

KG_CONVERSIONS = {
    'kg': Decimal('1'),
    'kgs': Decimal('1'),
    'kilogram': Decimal('1'),
    'kilograms': Decimal('1'),
    'g': Decimal('0.001'),
    'gram': Decimal('0.001'),
    'grams': Decimal('0.001'),
    'lb': Decimal('0.45359237'),
    'lbs': Decimal('0.45359237'),
    'pound': Decimal('0.45359237'),
    'pounds': Decimal('0.45359237'),
}


class MatchingError(ValueError):
    """Raised when a donation cannot be matched in its current state."""


def haversine_distance_km(latitude_a, longitude_a, latitude_b, longitude_b) -> float:
    """Return great-circle distance between two latitude/longitude pairs."""
    latitude_a, longitude_a, latitude_b, longitude_b = map(
        float, (latitude_a, longitude_a, latitude_b, longitude_b)
    )
    if not (-90 <= latitude_a <= 90 and -90 <= latitude_b <= 90):
        raise ValueError('Latitude must be between -90 and 90 degrees.')
    if not (-180 <= longitude_a <= 180 and -180 <= longitude_b <= 180):
        raise ValueError('Longitude must be between -180 and 180 degrees.')

    lat_a, lat_b = radians(latitude_a), radians(latitude_b)
    delta_lat = lat_b - lat_a
    delta_lon = radians(longitude_b - longitude_a)
    haversine = sin(delta_lat / 2) ** 2 + cos(lat_a) * cos(lat_b) * sin(delta_lon / 2) ** 2
    return 6371.0088 * 2 * asin(sqrt(min(1.0, haversine)))


def _normalized_weights() -> dict[str, float]:
    configured = getattr(settings, 'MATCHING_WEIGHTS', DEFAULT_WEIGHTS)
    weights = {key: float(configured.get(key, default)) for key, default in DEFAULT_WEIGHTS.items()}
    if any(weight < 0 for weight in weights.values()) or sum(weights.values()) <= 0:
        raise ValueError('Matching weights must be non-negative and have a positive total.')
    total = sum(weights.values())
    return {key: weight / total for key, weight in weights.items()}


def weighted_match_score(factor_scores: dict[str, float], weights: dict[str, float] | None = None) -> Decimal:
    """Combine 0-100 normalized factor scores into a weighted ranking score."""
    active_weights = weights or _normalized_weights()
    total_weight = sum(active_weights.values())
    if total_weight <= 0:
        raise ValueError('At least one positive matching weight is required.')
    score = sum(float(factor_scores[key]) * weight for key, weight in active_weights.items()) / total_weight
    return Decimal(str(round(max(0.0, min(100.0, score)), 2)))


def _quantity_kg(donation: FoodDonation) -> Decimal | None:
    conversion = KG_CONVERSIONS.get(donation.unit.strip().casefold())
    if conversion is None:
        return None
    return Decimal(donation.quantity) * conversion


def _remaining_shelf_life_hours(donation: FoodDonation, now) -> float:
    return max(0.0, (donation.expiry_time - now).total_seconds() / 3600)


def _factor_explanations(factor_scores: dict[str, float], weights: dict[str, float], distance_km, remaining_hours, capacity_ratio) -> list[str]:
    if distance_km is None:
        distance_detail = 'Distance unavailable; a neutral score was used.'
    else:
        distance_detail = f'Distance is {distance_km:.2f} km.'
    capacity_detail = f'Estimated capacity use is {capacity_ratio:.1f}%.'
    urgency_detail = f'{remaining_hours:.1f} hours remain before expiry.'
    details = {
        'distance': distance_detail,
        'food_compatibility': 'The NGO explicitly accepts this donation category.',
        'urgency': urgency_detail,
        'capacity': capacity_detail,
        'current_demand': 'Based on the NGO-maintained current demand score.',
        'reliability': 'Based on the administratively maintained reliability score.',
    }
    return [
        f"{name.replace('_', ' ').title()}: {details[name]} Score {factor_scores[name]:.1f}/100; weight {weights[name] * 100:.0f}%."
        for name in weights
    ]


def _score_profile(donation: FoodDonation, profile: NGOMatchingProfile, now, weights, max_distance_km, urgency_horizon_hours):
    accepted = profile.accepted_categories.filter(pk=donation.category_id).exists()
    if not accepted:
        return None

    quantity_kg = _quantity_kg(donation)
    capacity_kg = Decimal(profile.capacity_kg)
    if quantity_kg is None or capacity_kg <= 0 or quantity_kg > capacity_kg:
        return None

    distance_km = None
    if donation.latitude is not None and donation.longitude is not None and profile.latitude is not None and profile.longitude is not None:
        distance_km = haversine_distance_km(donation.latitude, donation.longitude, profile.latitude, profile.longitude)
        distance_score = max(0.0, 100.0 * (1.0 - min(distance_km / max_distance_km, 1.0)))
    else:
        # Preserve eligible matches, but do not treat missing coordinates as nearby.
        distance_score = 50.0

    remaining_hours = _remaining_shelf_life_hours(donation, now)
    urgency_score = max(0.0, 100.0 * (1.0 - min(remaining_hours / urgency_horizon_hours, 1.0)))
    capacity_ratio = float(quantity_kg / capacity_kg * 100)
    factor_scores = {
        'distance': round(distance_score, 2),
        'food_compatibility': 100.0,
        'urgency': round(urgency_score, 2),
        'capacity': round(max(0.0, 100.0 - capacity_ratio), 2),
        'current_demand': float(profile.current_demand_score),
        'reliability': float(profile.reliability_score),
    }
    return {
        'ngo': profile.ngo,
        'match_score': weighted_match_score(factor_scores, weights),
        'factor_scores': factor_scores,
        'factor_weights': weights,
        'distance_km': round(distance_km, 2) if distance_km is not None else None,
        'explanation': _factor_explanations(factor_scores, weights, distance_km, remaining_hours, capacity_ratio),
    }


def rank_eligible_ngos(donation: FoodDonation, now=None) -> list[dict]:
    """Score verified, active NGOs with configured category and sufficient capacity."""
    now = now or timezone.now()
    weights = _normalized_weights()
    max_distance_km = float(getattr(settings, 'MATCHING_MAX_DISTANCE_KM', 100.0))
    urgency_horizon_hours = float(getattr(settings, 'MATCHING_URGENCY_HORIZON_HOURS', 72.0))
    if max_distance_km <= 0 or urgency_horizon_hours <= 0:
        raise ValueError('Matching distance and urgency horizons must be positive.')

    profiles = (
        NGOMatchingProfile.objects.filter(
            is_active=True,
            ngo__is_active=True,
            ngo__role=User.Role.NGO,
            ngo__ngo_profile__is_verified=True,
            ngo__ngo_verification__status=NGOVerification.Status.APPROVED,
            accepted_categories=donation.category,
        )
        .select_related('ngo', 'ngo__ngo_profile', 'ngo__ngo_verification')
        .prefetch_related('accepted_categories')
        .distinct()
    )
    matches = []
    for profile in profiles:
        scored = _score_profile(donation, profile, now, weights, max_distance_km, urgency_horizon_hours)
        if scored:
            matches.append(scored)
    return sorted(matches, key=lambda item: (-item['match_score'], item['ngo'].pk))


def generate_recommendations(donation_id: int, limit: int = 10) -> list[NGORecommendation]:
    """Persist or refresh scored NGO recommendations for an available donation."""
    now = timezone.now()
    with transaction.atomic():
        donation = get_object_or_404(FoodDonation.objects.select_for_update(), pk=donation_id)
        if donation.status != FoodDonation.DonationStatus.AVAILABLE or donation.expiry_time <= now:
            raise MatchingError('Recommendations can only be generated for unexpired available donations.')

        ranked = rank_eligible_ngos(donation, now=now)
        active = {
            item.ngo_id: item
            for item in NGORecommendation.objects.select_for_update().filter(
                donation=donation,
                status=NGORecommendation.Status.RECOMMENDED,
            )
        }
        refreshed_ids = set()
        for result in ranked:
            ngo = result['ngo']
            recommendation = active.pop(ngo.pk, None)
            if recommendation is None:
                recommendation = NGORecommendation.objects.create(donation=donation, ngo=ngo, **{
                    key: result[key] for key in ('match_score', 'factor_scores', 'factor_weights', 'distance_km', 'explanation')
                })
                from apps.notifications.services import create_notification

                create_notification(
                    recipient=ngo,
                    title='New donation recommendation',
                    message=f'{donation.food_name} may fit your organization. Review the recommendation and its factors.',
                    event_code='NGO_MATCH_GENERATED',
                    notification_type='INFO',
                    donation=donation,
                    action_url='/dashboard/ngo',
                )
            else:
                for field in ('match_score', 'factor_scores', 'factor_weights', 'distance_km', 'explanation'):
                    setattr(recommendation, field, result[field])
                recommendation.save(update_fields=[
                    'match_score', 'factor_scores', 'factor_weights', 'distance_km', 'explanation', 'updated_at'
                ])
            refreshed_ids.add(recommendation.pk)

        for stale in active.values():
            stale.status = NGORecommendation.Status.SUPERSEDED
            stale.save(update_fields=['status', 'updated_at'])

        return list(
            NGORecommendation.objects.filter(pk__in=refreshed_ids)
            .select_related('donation__category', 'ngo__ngo_profile')
            .order_by('-match_score', 'ngo__ngo_profile__organization_name', 'ngo_id')[:limit]
        )


def accept_recommendation(recommendation_id: int, ngo: User) -> NGORecommendation:
    """Accept a recommendation and transition the donation atomically."""
    donation_id = NGORecommendation.objects.filter(pk=recommendation_id, ngo=ngo).values_list('donation_id', flat=True).first()
    if donation_id is None:
        raise MatchingError('Recommendation not found for this NGO.')
    try:
        with transaction.atomic():
            # Lock the shared donation before the recommendation, matching generation's
            # lock order. The compare-and-set below is also the final concurrency guard.
            donation = get_object_or_404(FoodDonation.objects.select_for_update(), pk=donation_id)
            recommendation = get_object_or_404(
                NGORecommendation.objects.select_for_update(),
                pk=recommendation_id,
                ngo=ngo,
                status=NGORecommendation.Status.RECOMMENDED,
            )
            if not ngo.is_active or not NGOProfile.objects.filter(user=ngo, is_verified=True).exists() or not NGOVerification.objects.filter(ngo=ngo, status=NGOVerification.Status.APPROVED).exists():
                raise MatchingError('Only active, verified NGOs can accept recommendations.')

            if donation.expiry_time <= timezone.now():
                raise MatchingError('This donation has expired and can no longer be accepted.')
            if donation.status != FoodDonation.DonationStatus.AVAILABLE or donation.accepted_ngo_id is not None:
                raise MatchingError('This donation is no longer available for acceptance.')
            try:
                matching_profile = NGOMatchingProfile.objects.select_for_update().get(ngo=ngo, is_active=True)
            except NGOMatchingProfile.DoesNotExist as exc:
                raise MatchingError('The NGO matching profile is inactive or unavailable.') from exc
            quantity_kg = _quantity_kg(donation)
            if (
                quantity_kg is None
                or quantity_kg > matching_profile.capacity_kg
                or not matching_profile.accepted_categories.filter(pk=donation.category_id).exists()
            ):
                raise MatchingError('The NGO no longer meets this donation\'s category and capacity requirements.')

            now = timezone.now()
            claimed = FoodDonation.objects.filter(
                pk=donation.pk,
                status=FoodDonation.DonationStatus.AVAILABLE,
                accepted_ngo__isnull=True,
                expiry_time__gt=now,
            ).update(
                status=FoodDonation.DonationStatus.MATCHED,
                accepted_ngo=ngo,
                updated_at=now,
            )
            if claimed != 1:
                raise MatchingError('Another NGO has already claimed this donation.')
            DonationStatusHistory.objects.create(
                donation=donation,
                previous_status=FoodDonation.DonationStatus.AVAILABLE,
                new_status=FoodDonation.DonationStatus.MATCHED,
                changed_by=ngo,
                note='Matched to a verified NGO.',
            )
            donation.status = FoodDonation.DonationStatus.MATCHED
            donation.accepted_ngo = ngo
            donation = transition_donation_status(
                donation,
                FoodDonation.DonationStatus.ACCEPTED,
                actor=ngo,
                note='Accepted through the NGO matching dashboard.',
            )

            NGORecommendation.objects.filter(
                donation=donation,
                status=NGORecommendation.Status.RECOMMENDED,
            ).exclude(pk=recommendation.pk).update(status=NGORecommendation.Status.SUPERSEDED, updated_at=now)
            recommendation.status = NGORecommendation.Status.ACCEPTED
            recommendation.accepted_at = now
            recommendation.save(update_fields=['status', 'accepted_at', 'updated_at'])
            return recommendation
    except IntegrityError as exc:
        raise MatchingError('This donation has already been accepted by another NGO.') from exc


def decline_recommendation(recommendation_id: int, ngo: User) -> NGORecommendation:
    with transaction.atomic():
        recommendation = get_object_or_404(
            NGORecommendation.objects.select_for_update(),
            pk=recommendation_id,
            ngo=ngo,
            status=NGORecommendation.Status.RECOMMENDED,
        )
        recommendation.status = NGORecommendation.Status.DECLINED
        recommendation.save(update_fields=['status', 'updated_at'])
        from apps.notifications.services import create_notification

        create_notification(
            recipient=recommendation.donation.donor,
            title='NGO declined recommendation',
            message=f'{ngo.ngo_profile.organization_name} declined {recommendation.donation.food_name}.',
            event_code='DONATION_REJECTED',
            notification_type='WARNING',
            donation=recommendation.donation,
            action_url=f'/donations/{recommendation.donation_id}',
        )
        return recommendation
