from __future__ import annotations

import hashlib
import re
from datetime import timedelta
from difflib import SequenceMatcher

from django.conf import settings
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.donations.models import DonationStatusHistory, FoodDonation

from .models import FraudAlert

RULE_VERSION = 'fraud-rules-v1'
UNIT_TO_KG = {
    'kg': 1.0, 'kgs': 1.0, 'kilogram': 1.0, 'kilograms': 1.0,
    'g': 0.001, 'gram': 0.001, 'grams': 0.001,
    'lb': 0.45359237, 'lbs': 0.45359237, 'pound': 0.45359237, 'pounds': 0.45359237,
}


def _setting(name, default):
    return getattr(settings, name, default)


def _risk_level(score: int) -> str:
    thresholds = _setting('FRAUD_RISK_THRESHOLDS', {'medium': 25, 'high': 55, 'critical': 80})
    if score >= thresholds['critical']:
        return FraudAlert.AlertSeverity.CRITICAL
    if score >= thresholds['high']:
        return FraudAlert.AlertSeverity.HIGH
    if score >= thresholds['medium']:
        return FraudAlert.AlertSeverity.MEDIUM
    return FraudAlert.AlertSeverity.LOW


def _deduplication_key(alert_type: str, actor_id: int, donation_id: int | None) -> str:
    issue_scope = f'donation:{donation_id}' if donation_id is not None else 'account'
    return hashlib.sha256(f'{alert_type}:{actor_id}:{issue_scope}'.encode('utf-8')).hexdigest()


def _persist_unresolved_alert(*, alert_type, actor, donation, reasons, score):
    if not reasons:
        return None
    key = _deduplication_key(alert_type, actor.pk, donation.pk if donation else None)
    level = _risk_level(score)
    reason_text = '; '.join(item['detail'] for item in reasons)
    now = timezone.now()
    with transaction.atomic():
        alert = FraudAlert.objects.select_for_update().filter(
            deduplication_key=key,
            status__in=[FraudAlert.AlertStatus.OPEN, FraudAlert.AlertStatus.REVIEWING],
        ).first()
        if alert:
            alert.risk_score = max(alert.risk_score, score)
            alert.severity = _risk_level(alert.risk_score)
            alert.reason = reason_text
            alert.reasons = reasons
            alert.occurrence_count += 1
            alert.last_seen_at = now
            alert.save(update_fields=['risk_score', 'severity', 'reason', 'reasons', 'occurrence_count', 'last_seen_at', 'updated_at'])
            return alert

        try:
            # Nested atomic provides a savepoint so a concurrent unique-constraint
            # race does not leave the surrounding transaction unusable.
            with transaction.atomic():
                alert = FraudAlert.objects.create(
                    actor=actor,
                    donation=donation,
                    alert_type=alert_type,
                    severity=level,
                    risk_score=score,
                    reason=reason_text,
                    reasons=reasons,
                    deduplication_key=key,
                    detection_method='RULE_BASED',
                    rule_version=RULE_VERSION,
                )
                from apps.notifications.services import notify_admins

                notify_admins(
                    title='Fraud alert needs review',
                    message=f'A {level.lower()} rule-based alert was generated for donation #{donation.pk}.' if donation else f'A {level.lower()} account activity alert was generated.',
                    event_code='FRAUD_ALERT_GENERATED',
                    notification_type='ALERT',
                    donation=donation,
                    action_url='/admin/fraud-alerts',
                )
                return alert
        except IntegrityError:
            alert = FraudAlert.objects.select_for_update().get(
                deduplication_key=key,
                status__in=[FraudAlert.AlertStatus.OPEN, FraudAlert.AlertStatus.REVIEWING],
            )
            alert.risk_score = max(alert.risk_score, score)
            alert.severity = _risk_level(alert.risk_score)
            alert.reason = reason_text
            alert.reasons = reasons
            alert.occurrence_count += 1
            alert.last_seen_at = now
            alert.save(update_fields=['risk_score', 'severity', 'reason', 'reasons', 'occurrence_count', 'last_seen_at', 'updated_at'])
            return alert


def _normalized_food_name(value: str) -> str:
    return re.sub(r'[^a-z0-9]+', ' ', (value or '').casefold()).strip()


def _similar_recent_donations(donation: FoodDonation, now):
    window = timedelta(hours=int(_setting('FRAUD_DUPLICATE_WINDOW_HOURS', 48)))
    candidates = FoodDonation.objects.filter(
        donor_id=donation.donor_id,
        category_id=donation.category_id,
        created_at__gte=now - window,
        created_at__lt=donation.created_at,
    ).exclude(pk=donation.pk).only('id', 'food_name', 'quantity', 'unit')[:100]
    new_name = _normalized_food_name(donation.food_name)
    threshold = float(_setting('FRAUD_SIMILARITY_THRESHOLD', 0.85))
    max_quantity_delta = float(_setting('FRAUD_DUPLICATE_QUANTITY_DELTA', 0.25))
    new_unit_factor = UNIT_TO_KG.get(donation.unit.casefold())
    new_quantity = float(donation.quantity) * new_unit_factor if new_unit_factor else None
    for previous in candidates:
        prior_name = _normalized_food_name(previous.food_name)
        similarity = SequenceMatcher(None, new_name, prior_name).ratio()
        old_unit_factor = UNIT_TO_KG.get(previous.unit.casefold())
        old_quantity = float(previous.quantity) * old_unit_factor if old_unit_factor else None
        quantity_matches = (
            new_quantity is None or old_quantity is None
            or max(new_quantity, old_quantity, 0.01) and abs(new_quantity - old_quantity) / max(new_quantity, old_quantity, 0.01) <= max_quantity_delta
        )
        if similarity >= threshold and quantity_matches:
            return previous, similarity
    return None, 0.0


def evaluate_donation_risk(donation: FoodDonation, *, event: str = 'SUBMISSION', now=None) -> dict:
    """Evaluate a donation using deterministic rules and persist deduplicated alerts.

    Returns internal assessment data for service callers. Do not serialize this in
    donor/NGO API responses; only the admin review endpoints expose alert details.
    """
    now = now or timezone.now()
    donation_reasons = []
    activity_reasons = []
    donation_score = 0
    activity_score = 0
    max_quantity_kg = float(_setting('FRAUD_MAX_DONATION_KG', 500.0))
    factor = UNIT_TO_KG.get(donation.unit.casefold())
    if factor is not None and float(donation.quantity) * factor > max_quantity_kg:
        donation_score += int(_setting('FRAUD_POINTS_UNREALISTIC_QUANTITY', 40))
        donation_reasons.append({
            'code': 'UNREALISTIC_QUANTITY',
            'detail': 'Donation quantity exceeds the configured plausibility limit.',
        })

    duplicate, similarity = _similar_recent_donations(donation, now)
    if duplicate:
        donation_score += int(_setting('FRAUD_POINTS_SIMILAR_DONATION', 35))
        donation_reasons.append({
            'code': 'SIMILAR_DONATION',
            'detail': f'Donation is highly similar to a recent submission (similarity {similarity:.2f}).',
        })

    cancellation_days = int(_setting('FRAUD_CANCELLATION_WINDOW_DAYS', 30))
    cancellations = DonationStatusHistory.objects.filter(
        donation__donor_id=donation.donor_id,
        new_status=FoodDonation.DonationStatus.CANCELLED,
        created_at__gte=now - timedelta(days=cancellation_days),
    ).count()
    cancellation_threshold = int(_setting('FRAUD_REPEATED_CANCELLATION_COUNT', 3))
    if cancellations >= cancellation_threshold:
        activity_score += int(_setting('FRAUD_POINTS_REPEATED_CANCELLATIONS', 30))
        activity_reasons.append({
            'code': 'REPEATED_CANCELLATIONS',
            'detail': f'{cancellations} donation cancellations occurred in the last {cancellation_days} days.',
        })

    submission_hours = int(_setting('FRAUD_SUBMISSION_WINDOW_HOURS', 24))
    recent_submissions = FoodDonation.objects.filter(
        donor_id=donation.donor_id,
        created_at__gte=now - timedelta(hours=submission_hours),
        created_at__lte=now,
    ).count()
    submission_threshold = int(_setting('FRAUD_FREQUENT_SUBMISSION_COUNT', 10))
    if recent_submissions >= submission_threshold:
        activity_score += int(_setting('FRAUD_POINTS_FREQUENT_SUBMISSIONS', 20))
        activity_reasons.append({
            'code': 'FREQUENT_SUBMISSIONS',
            'detail': f'{recent_submissions} donation submissions occurred in the last {submission_hours} hours.',
        })

    activity_days = int(_setting('FRAUD_ABNORMAL_ACTIVITY_WINDOW_DAYS', 7))
    activity_count = FoodDonation.objects.filter(
        donor_id=donation.donor_id,
        created_at__gte=now - timedelta(days=activity_days),
        created_at__lte=now,
    ).count()
    activity_threshold = int(_setting('FRAUD_ABNORMAL_ACTIVITY_COUNT', 20))
    if activity_count >= activity_threshold:
        activity_score += int(_setting('FRAUD_POINTS_ABNORMAL_ACTIVITY', 25))
        activity_reasons.append({
            'code': 'ABNORMAL_DONATION_ACTIVITY',
            'detail': f'{activity_count} donation submissions occurred in the last {activity_days} days.',
        })

    complaint_days = int(_setting('FRAUD_COMPLAINT_WINDOW_DAYS', 90))
    # Complaints are counted only when attached to the donor's donations; the
    # complainant's own complaint volume is never treated as suspicious.
    try:
        from apps.feedback.models import Complaint

        complaint_count = Complaint.objects.filter(
            donation__donor_id=donation.donor_id,
            status__in=['OPEN', 'REVIEWING'],
            created_at__gte=now - timedelta(days=complaint_days),
        ).values('id').distinct().count()
    except Exception as exc:
        # Keep ordinary donation handling operational until a deployment has
        # applied the feedback migration; never silently fabricate complaint data.
        from django.db.utils import OperationalError, ProgrammingError
        if not isinstance(exc, (OperationalError, ProgrammingError)):
            raise
        complaint_count = 0
    complaint_threshold = int(_setting('FRAUD_REPEATED_COMPLAINT_COUNT', 3))
    if complaint_count >= complaint_threshold:
        activity_score += int(_setting('FRAUD_POINTS_REPEATED_COMPLAINTS', 35))
        activity_reasons.append({
            'code': 'REPEATED_COMPLAINTS',
            'detail': f'{complaint_count} open complaints reference this donor\'s donations in the last {complaint_days} days.',
        })

    donation_score = max(0, min(100, donation_score))
    activity_score = max(0, min(100, activity_score))
    alerts = []
    if donation_reasons:
        alerts.append(_persist_unresolved_alert(
            alert_type='DONATION_PATTERN', actor=donation.donor, donation=donation,
            reasons=donation_reasons, score=donation_score,
        ))
    if activity_reasons:
        alerts.append(_persist_unresolved_alert(
            alert_type='ACCOUNT_ACTIVITY', actor=donation.donor, donation=None,
            reasons=activity_reasons, score=activity_score,
        ))

    all_reasons = donation_reasons + activity_reasons
    overall_score = min(100, donation_score + activity_score)
    return {
        'risk_score': overall_score,
        'risk_level': _risk_level(overall_score),
        'reasons': all_reasons,
        'review_status': 'FLAGGED' if all_reasons else 'NOT_FLAGGED',
        'detection_method': 'RULE_BASED',
        'alerts': [alert for alert in alerts if alert is not None],
        'event': event,
    }
