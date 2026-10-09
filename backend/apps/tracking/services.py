from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.accounts.models import NGOProfile
from apps.donations.models import DonationStatusHistory, FoodDonation
from apps.donations.services import transition_donation_status

from .models import Beneficiary, DeliveryLog, Pickup, PickupStatusHistory

VALID_PICKUP_TRANSITIONS = {
    Pickup.PickupStatus.SCHEDULED: {Pickup.PickupStatus.ACCEPTED, Pickup.PickupStatus.CANCELLED},
    Pickup.PickupStatus.ACCEPTED: {Pickup.PickupStatus.IN_TRANSIT, Pickup.PickupStatus.CANCELLED},
    Pickup.PickupStatus.IN_TRANSIT: {Pickup.PickupStatus.PICKED_UP, Pickup.PickupStatus.CANCELLED},
    Pickup.PickupStatus.PICKED_UP: {Pickup.PickupStatus.DELIVERED},
    Pickup.PickupStatus.DELIVERED: set(),
    Pickup.PickupStatus.CANCELLED: set(),
}


class PickupWorkflowError(ValueError):
    pass


def _get_locked_pickup(pickup_id):
    pickup_data = Pickup.objects.filter(pk=pickup_id).values('donation_id').first()
    if pickup_data is None:
        raise PickupWorkflowError('Pickup not found.')
    donation = FoodDonation.objects.select_for_update().filter(pk=pickup_data['donation_id']).first()
    if donation is None:
        raise PickupWorkflowError('Donation not found.')
    pickup = Pickup.objects.select_for_update().select_related('ngo', 'assigned_volunteer').filter(
        pk=pickup_id,
        donation=donation,
    ).first()
    if pickup is None:
        raise PickupWorkflowError('Pickup not found.')
    return donation, pickup


def _record_pickup_status(pickup, previous, next_status, actor, note):
    PickupStatusHistory.objects.create(
        pickup=pickup,
        previous_status=previous,
        new_status=next_status,
        changed_by=actor,
        note=note,
    )


def schedule_ngo_pickup(donation_id, ngo, pickup_window_start, pickup_window_end, notes=''):
    try:
        with transaction.atomic():
            donation = FoodDonation.objects.select_for_update().filter(pk=donation_id).first()
            if donation is None:
                raise PickupWorkflowError('Donation not found.')
            if donation.accepted_ngo_id != ngo.pk or donation.status != FoodDonation.DonationStatus.ACCEPTED:
                raise PickupWorkflowError('This NGO is not the active assignee for the donation.')
            profile = NGOProfile.objects.get(user=ngo)
            beneficiary, _ = Beneficiary.objects.get_or_create(
                name=profile.organization_name,
                address=profile.address,
                defaults={'phone_number': ngo.phone_number, 'city': profile.city, 'state': profile.state},
            )
            pickup = Pickup.objects.create(
                donation=donation,
                ngo=ngo,
                beneficiary=beneficiary,
                pickup_window_start=pickup_window_start,
                pickup_window_end=pickup_window_end,
                notes=notes,
            )
            transition_donation_status(
                donation,
                FoodDonation.DonationStatus.PICKUP_SCHEDULED,
                actor=ngo,
                note='Pickup scheduled by the accepted NGO.',
            )
            _record_pickup_status(pickup, '', Pickup.PickupStatus.SCHEDULED, ngo, 'Pickup scheduled by the accepted NGO.')
            return pickup
    except IntegrityError as exc:
        raise PickupWorkflowError('A pickup is already scheduled for this donation.') from exc


def accept_pickup(pickup_id, volunteer):
    with transaction.atomic():
        _, pickup = _get_locked_pickup(pickup_id)
        if not volunteer.is_active:
            raise PickupWorkflowError('Inactive volunteers cannot accept pickups.')
        if pickup.status != Pickup.PickupStatus.SCHEDULED:
            raise PickupWorkflowError('Only scheduled pickups can be accepted.')
        if pickup.assigned_volunteer_id not in (None, volunteer.pk):
            raise PickupWorkflowError('This pickup is assigned to another volunteer.')
        previous = pickup.status
        pickup.assigned_volunteer = volunteer
        pickup.status = Pickup.PickupStatus.ACCEPTED
        pickup.accepted_at = timezone.now()
        pickup.save(update_fields=['assigned_volunteer', 'status', 'accepted_at', 'updated_at'])
        _record_pickup_status(pickup, previous, pickup.status, volunteer, 'Pickup accepted by assigned volunteer.')
        from apps.notifications.services import create_notification

        for recipient in (pickup.donation.donor, pickup.ngo):
            create_notification(
                recipient=recipient,
                title='Volunteer assigned to pickup',
                message=f'{volunteer.get_full_name() or volunteer.username} accepted the pickup for {pickup.donation.food_name}.',
                event_code='VOLUNTEER_ASSIGNED',
                notification_type='INFO',
                donation=pickup.donation,
                action_url='/dashboard/ngo' if recipient.pk == pickup.ngo_id else f'/donations/{pickup.donation_id}',
            )
        return pickup


def transition_pickup(pickup_id, next_status, actor, note='', proof_file=None):
    with transaction.atomic():
        donation, pickup = _get_locked_pickup(pickup_id)
        if actor.role == 'VOLUNTEER' and pickup.assigned_volunteer_id != actor.pk:
            raise PickupWorkflowError('Volunteers may update only pickups assigned to them.')
        if actor.role == 'NGO' and pickup.ngo_id != actor.pk:
            raise PickupWorkflowError('NGOs may update only pickups related to their donations.')
        if actor.role not in {'VOLUNTEER', 'NGO', 'ADMIN'}:
            raise PickupWorkflowError('This account cannot update pickup status.')
        if next_status not in VALID_PICKUP_TRANSITIONS.get(pickup.status, set()):
            raise PickupWorkflowError(f'Invalid pickup transition from {pickup.status} to {next_status}.')

        now = timezone.now()
        previous = pickup.status
        if next_status == Pickup.PickupStatus.PICKED_UP:
            if donation.status != FoodDonation.DonationStatus.PICKUP_SCHEDULED:
                raise PickupWorkflowError('Donation must have a scheduled pickup before collection confirmation.')
            transition_donation_status(donation, FoodDonation.DonationStatus.PICKED_UP, actor=actor, note=note or 'Volunteer confirmed collection.')
            pickup.picked_up_at = now
        elif next_status == Pickup.PickupStatus.DELIVERED:
            if donation.status != FoodDonation.DonationStatus.PICKED_UP:
                raise PickupWorkflowError('Donation must be collected before delivery confirmation.')
            transition_donation_status(donation, FoodDonation.DonationStatus.DELIVERED, actor=actor, note=note or 'Volunteer confirmed delivery.')
            pickup.delivered_at = now
            DeliveryLog.objects.create(
                pickup=pickup,
                delivered_by=actor,
                delivered_at=now,
                condition='GOOD',
                comment=note,
                proof_file=proof_file,
            )
        elif next_status == Pickup.PickupStatus.CANCELLED:
            if donation.status not in {FoodDonation.DonationStatus.ACCEPTED, FoodDonation.DonationStatus.PICKUP_SCHEDULED}:
                raise PickupWorkflowError('A pickup cannot be cancelled after collection has begun.')
            if donation.status != FoodDonation.DonationStatus.CANCELLED:
                transition_donation_status(donation, FoodDonation.DonationStatus.CANCELLED, actor=actor, note=note or 'Pickup cancelled.')
            pickup.cancelled_at = now

        pickup.status = next_status
        pickup.save(update_fields=['status', 'picked_up_at', 'delivered_at', 'cancelled_at', 'updated_at'])
        _record_pickup_status(pickup, previous, next_status, actor, note)
        return pickup


def confirm_ngo_received(pickup_id, ngo):
    with transaction.atomic():
        donation, pickup = _get_locked_pickup(pickup_id)
        if pickup.ngo_id != ngo.pk or donation.accepted_ngo_id != ngo.pk:
            raise PickupWorkflowError('This NGO is not the assignee for the donation.')
        if pickup.status != Pickup.PickupStatus.DELIVERED or donation.status != FoodDonation.DonationStatus.DELIVERED:
            raise PickupWorkflowError('The volunteer must confirm delivery before the NGO can confirm receipt.')
        donation = transition_donation_status(
            donation,
            FoodDonation.DonationStatus.COMPLETED,
            actor=ngo,
            note='NGO confirmed receipt of the food.',
        )
        pickup.received_at = timezone.now()
        pickup.save(update_fields=['received_at', 'updated_at'])
        return pickup
