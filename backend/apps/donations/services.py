from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import DonationMatch, DonationRequest, DonationStatusHistory, FoodDonation

ACCESSIBLE_STATUSES = {
    FoodDonation.DonationStatus.AVAILABLE,
    FoodDonation.DonationStatus.MATCHED,
    FoodDonation.DonationStatus.ACCEPTED,
    FoodDonation.DonationStatus.PICKUP_SCHEDULED,
    FoodDonation.DonationStatus.PICKED_UP,
    FoodDonation.DonationStatus.DELIVERED,
    FoodDonation.DonationStatus.COMPLETED,
}

VALID_STATUS_TRANSITIONS = {
    FoodDonation.DonationStatus.AVAILABLE: {
        FoodDonation.DonationStatus.MATCHED,
        FoodDonation.DonationStatus.ACCEPTED,
        FoodDonation.DonationStatus.CANCELLED,
        FoodDonation.DonationStatus.EXPIRED,
    },
    FoodDonation.DonationStatus.MATCHED: {
        FoodDonation.DonationStatus.ACCEPTED,
        FoodDonation.DonationStatus.CANCELLED,
        FoodDonation.DonationStatus.EXPIRED,
    },
    FoodDonation.DonationStatus.ACCEPTED: {
        FoodDonation.DonationStatus.PICKUP_SCHEDULED,
        FoodDonation.DonationStatus.CANCELLED,
        FoodDonation.DonationStatus.REJECTED,
    },
    FoodDonation.DonationStatus.PICKUP_SCHEDULED: {
        FoodDonation.DonationStatus.PICKED_UP,
        FoodDonation.DonationStatus.CANCELLED,
    },
    FoodDonation.DonationStatus.PICKED_UP: {
        FoodDonation.DonationStatus.DELIVERED,
        FoodDonation.DonationStatus.COMPLETED,
    },
    FoodDonation.DonationStatus.DELIVERED: {
        FoodDonation.DonationStatus.COMPLETED,
    },
    FoodDonation.DonationStatus.COMPLETED: set(),
    FoodDonation.DonationStatus.CANCELLED: set(),
    FoodDonation.DonationStatus.EXPIRED: set(),
    FoodDonation.DonationStatus.REJECTED: set(),
}


def can_edit_donation(donation):
    return donation.status in {
        FoodDonation.DonationStatus.AVAILABLE,
        FoodDonation.DonationStatus.MATCHED,
        FoodDonation.DonationStatus.ACCEPTED,
        FoodDonation.DonationStatus.PICKUP_SCHEDULED,
    }


def mark_expired_if_needed(donation):
    if donation.expiry_time and donation.expiry_time <= timezone.now() and donation.status not in {
        FoodDonation.DonationStatus.EXPIRED,
        FoodDonation.DonationStatus.CANCELLED,
        FoodDonation.DonationStatus.COMPLETED,
        FoodDonation.DonationStatus.PICKED_UP,
    }:
        return transition_donation_status(donation, FoodDonation.DonationStatus.EXPIRED, actor=None, note='Donation expired automatically.')
    return donation


def transition_donation_status(donation, next_status, actor=None, note=''):
    current_status = donation.status
    if current_status == next_status:
        return donation

    if current_status in {FoodDonation.DonationStatus.COMPLETED, FoodDonation.DonationStatus.PICKED_UP} and next_status == FoodDonation.DonationStatus.AVAILABLE:
        raise ValidationError({'status': 'A completed or picked-up donation cannot be reset to AVAILABLE.'})

    allowed = VALID_STATUS_TRANSITIONS.get(current_status, set())
    if next_status not in allowed:
        raise ValidationError({
            'status': f'Invalid status transition from {current_status} to {next_status}.',
        })

    with transaction.atomic():
        donation.status = next_status
        donation.save(update_fields=['status', 'updated_at'])
        DonationStatusHistory.objects.create(
            donation=donation,
            previous_status=current_status,
            new_status=next_status,
            changed_by=actor,
            note=note,
        )
        notification_details = {
            FoodDonation.DonationStatus.MATCHED: ('Donation matched', 'MATCHED'),
            FoodDonation.DonationStatus.ACCEPTED: ('Donation accepted', 'ACCEPTED'),
            FoodDonation.DonationStatus.PICKUP_SCHEDULED: ('Pickup scheduled', 'PICKUP_SCHEDULED'),
            FoodDonation.DonationStatus.PICKED_UP: ('Food picked up', 'PICKED_UP'),
            FoodDonation.DonationStatus.DELIVERED: ('Food delivered', 'DELIVERED'),
            FoodDonation.DonationStatus.COMPLETED: ('Donation completed', 'COMPLETED'),
            FoodDonation.DonationStatus.CANCELLED: ('Donation cancelled', 'CANCELLED'),
            FoodDonation.DonationStatus.REJECTED: ('Donation request rejected', 'REJECTED'),
        }.get(next_status)
        if notification_details:
            from apps.notifications.services import create_notification

            title, event_code = notification_details
            recipients = [donation.donor]
            if donation.accepted_ngo_id:
                recipients.append(donation.accepted_ngo)
            for recipient in {item.pk: item for item in recipients if item and (actor is None or item.pk != actor.pk)}.values():
                create_notification(
                    recipient=recipient,
                    title=title,
                    message=f'{donation.food_name} is now {next_status.replace("_", " ").lower()}.',
                    event_code=event_code,
                    notification_type='ALERT' if next_status in {FoodDonation.DonationStatus.CANCELLED, FoodDonation.DonationStatus.REJECTED} else 'INFO',
                    donation=donation,
                    action_url=f'/donations/{donation.pk}',
                )
    return donation


def decide_donation_request(request_id, donor, *, accept: bool):
    """Let the owning donor accept or reject an NGO request atomically."""
    from apps.accounts.models import NGOVerification, NGOProfile
    from apps.matching.models import NGORecommendation, NGOMatchingProfile

    donation_id = DonationRequest.objects.filter(pk=request_id, donation__donor=donor).values_list('donation_id', flat=True).first()
    if donation_id is None:
        raise ValidationError({'detail': 'Donation request not found for this donor.'})
    with transaction.atomic():
        donation = FoodDonation.objects.select_for_update().get(pk=donation_id, donor=donor)
        request = DonationRequest.objects.select_for_update().select_related('ngo').get(
            pk=request_id,
            donation=donation,
            status=DonationRequest.RequestStatus.PENDING,
        )
        if not accept:
            request.status = DonationRequest.RequestStatus.REJECTED
            request.save(update_fields=['status', 'updated_at'])
            from apps.notifications.services import create_notification

            create_notification(
                recipient=request.ngo,
                title='Donation request declined',
                message=f'The donor declined your request for {donation.food_name}.',
                event_code='DONATION_REQUEST_REJECTED',
                notification_type='WARNING',
                donation=donation,
                action_url='/dashboard/ngo',
            )
            return request
        if donation.expiry_time <= timezone.now():
            raise ValidationError({'detail': 'This donation has expired.'})
        if (
            not request.ngo.is_active
            or not NGOProfile.objects.filter(user=request.ngo, is_verified=True).exists()
            or not NGOVerification.objects.filter(ngo=request.ngo, status=NGOVerification.Status.APPROVED).exists()
        ):
            raise ValidationError({'detail': 'Only active, verified NGOs can accept donations.'})
        matching_profile = NGOMatchingProfile.objects.select_for_update().filter(ngo=request.ngo, is_active=True).first()
        conversions = {
            'kg': Decimal('1'), 'kgs': Decimal('1'), 'kilogram': Decimal('1'), 'kilograms': Decimal('1'),
            'g': Decimal('0.001'), 'gram': Decimal('0.001'), 'grams': Decimal('0.001'),
            'lb': Decimal('0.45359237'), 'lbs': Decimal('0.45359237'),
        }
        conversion = conversions.get(donation.unit.strip().casefold())
        quantity_kg = donation.quantity * conversion if conversion is not None else None
        if (
            matching_profile is None
            or quantity_kg is None
            or quantity_kg > matching_profile.capacity_kg
            or not matching_profile.accepted_categories.filter(pk=donation.category_id).exists()
        ):
            raise ValidationError({'detail': 'The NGO no longer meets this donation\'s category and capacity requirements.'})
        if request.requested_quantity != donation.quantity:
            raise ValidationError({'detail': 'Partial allocation is unsupported; a request must cover the full donation.'})

        now = timezone.now()
        claimed = FoodDonation.objects.filter(
            pk=donation.pk,
            status=FoodDonation.DonationStatus.AVAILABLE,
            accepted_ngo__isnull=True,
            expiry_time__gt=now,
        ).update(
            status=FoodDonation.DonationStatus.MATCHED,
            accepted_ngo=request.ngo,
            updated_at=now,
        )
        if claimed != 1:
            raise ValidationError({'detail': 'This donation has already been accepted by another organization.'})
        DonationStatusHistory.objects.create(
            donation=donation,
            previous_status=FoodDonation.DonationStatus.AVAILABLE,
            new_status=FoodDonation.DonationStatus.MATCHED,
            changed_by=donor,
            note='Donor accepted an NGO donation request.',
        )
        donation.status = FoodDonation.DonationStatus.MATCHED
        donation.accepted_ngo = request.ngo
        transition_donation_status(
            donation,
            FoodDonation.DonationStatus.ACCEPTED,
            actor=donor,
            note='Donation request accepted by the donor.',
        )
        request.status = DonationRequest.RequestStatus.ACCEPTED
        request.save(update_fields=['status', 'updated_at'])
        DonationMatch.objects.create(
            donation=donation,
            request=request,
            matched_by=donor,
            status=DonationMatch.MatchStatus.ACCEPTED,
            match_score=0,
            note='Accepted through NGO request workflow.',
        )
        competing_requests = list(DonationRequest.objects.filter(
            donation=donation,
            status=DonationRequest.RequestStatus.PENDING,
        ).exclude(pk=request.pk).select_related('ngo__ngo_profile'))
        DonationRequest.objects.filter(pk__in=[item.pk for item in competing_requests]).update(
            status=DonationRequest.RequestStatus.REJECTED,
            updated_at=now,
        )
        from apps.notifications.services import create_notification

        create_notification(
            recipient=request.ngo,
            title='Donation request accepted',
            message=f'The donor accepted your request for {donation.food_name}.',
            event_code='DONATION_REQUEST_ACCEPTED',
            notification_type='SUCCESS',
            donation=donation,
            action_url='/dashboard/ngo',
        )
        for competing in competing_requests:
            create_notification(
                recipient=competing.ngo,
                title='Donation no longer available',
                message=f'{donation.food_name} was assigned to another organization.',
                event_code='DONATION_REQUEST_REJECTED',
                notification_type='WARNING',
                donation=donation,
                action_url='/dashboard/ngo',
            )
        NGORecommendation.objects.filter(
            donation=donation,
            status=NGORecommendation.Status.RECOMMENDED,
        ).update(status=NGORecommendation.Status.SUPERSEDED, updated_at=now)
        return request
