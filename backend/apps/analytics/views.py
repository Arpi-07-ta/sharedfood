from decimal import Decimal

from django.db.models import Avg, Count, Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsVerifiedNGO
from apps.donations.models import FoodDonation
from apps.feedback.models import Feedback
from apps.tracking.models import Pickup


KG_CONVERSIONS = {
    'kg': Decimal('1'), 'kgs': Decimal('1'), 'kilogram': Decimal('1'), 'kilograms': Decimal('1'),
    'g': Decimal('0.001'), 'gram': Decimal('0.001'), 'grams': Decimal('0.001'),
    'lb': Decimal('0.45359237'), 'lbs': Decimal('0.45359237'),
}


class NGOAnalyticsView(APIView):
    permission_classes = [IsAuthenticated, IsVerifiedNGO]

    def get(self, request):
        donations = FoodDonation.objects.filter(accepted_ngo=request.user)
        completed = donations.filter(status=FoodDonation.DonationStatus.COMPLETED)
        received_kg = Decimal('0.00')
        for quantity, unit in completed.values_list('quantity', 'unit'):
            factor = KG_CONVERSIONS.get(unit.strip().casefold())
            if factor is not None:
                received_kg += Decimal(quantity) * factor
        pickup_counts = Pickup.objects.filter(ngo=request.user).aggregate(
            scheduled=Count('id', filter=Q(status=Pickup.PickupStatus.SCHEDULED)),
            completed=Count('id', filter=Q(status=Pickup.PickupStatus.DELIVERED)),
        )
        feedback = Feedback.objects.filter(user=request.user).aggregate(
            count=Count('id'),
            average_rating=Avg('rating'),
        )
        return Response({
            'accepted_donations': donations.count(),
            'active_donations': donations.filter(status__in=[
                FoodDonation.DonationStatus.ACCEPTED,
                FoodDonation.DonationStatus.PICKUP_SCHEDULED,
                FoodDonation.DonationStatus.PICKED_UP,
                FoodDonation.DonationStatus.DELIVERED,
            ]).count(),
            'completed_donations': completed.count(),
            'received_quantity_kg': str(received_kg.quantize(Decimal('0.01'))),
            'scheduled_pickups': pickup_counts['scheduled'],
            'completed_pickups': pickup_counts['completed'],
            'feedback_count': feedback['count'],
            'average_feedback_rating': round(feedback['average_rating'], 2) if feedback['average_rating'] is not None else None,
        })
