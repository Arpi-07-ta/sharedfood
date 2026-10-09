from decimal import Decimal

from rest_framework import serializers

from apps.donations.models import FoodDonation


class FoodWastePredictionSerializer(serializers.Serializer):
    food_category = serializers.CharField(max_length=120)
    quantity = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))
    preparation_time_hours = serializers.DecimalField(max_digits=6, decimal_places=2, min_value=Decimal('0.00'), required=False, allow_null=True)
    remaining_shelf_life_hours = serializers.DecimalField(max_digits=6, decimal_places=2, min_value=Decimal('0.00'))
    storage_condition = serializers.CharField(max_length=40)
    demand = serializers.DecimalField(max_digits=6, decimal_places=2, min_value=Decimal('0.00'), max_value=Decimal('100.00'))
    historical_wastage_rate = serializers.DecimalField(max_digits=6, decimal_places=2, min_value=Decimal('0.00'), max_value=Decimal('100.00'))
    donation_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_food_category(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError('Food category is required.')
        return cleaned.title()

    def validate_storage_condition(self, value):
        cleaned = value.strip().upper()
        valid = {'AMBIENT', 'REFRIGERATED', 'FROZEN', 'ROOM_TEMPERATURE'}
        if cleaned not in valid:
            raise serializers.ValidationError('Storage condition must be one of: AMBIENT, REFRIGERATED, FROZEN, ROOM_TEMPERATURE.')
        return cleaned

    def validate(self, attrs):
        donation_id = attrs.get('donation_id')
        if donation_id is not None:
            donation = FoodDonation.objects.filter(id=donation_id).first()
            if donation is None:
                raise serializers.ValidationError({'donation_id': 'Donation was not found.'})
            attrs['donation'] = donation
        return attrs


class UrgencyCalculationSerializer(serializers.Serializer):
    food_category = serializers.CharField(max_length=120)
    quantity = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))
    remaining_shelf_life_hours = serializers.DecimalField(max_digits=6, decimal_places=2, min_value=Decimal('0.00'))
    storage_condition = serializers.CharField(max_length=40)
    demand = serializers.DecimalField(max_digits=6, decimal_places=2, min_value=Decimal('0.00'), max_value=Decimal('100.00'))
    preparation_time_hours = serializers.DecimalField(max_digits=6, decimal_places=2, required=False, allow_null=True, min_value=Decimal('0.00'))
    donation_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_food_category(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError('Food category is required.')
        return cleaned.title()

    def validate_storage_condition(self, value):
        cleaned = value.strip().upper()
        valid = {'AMBIENT', 'REFRIGERATED', 'FROZEN', 'ROOM_TEMPERATURE'}
        if cleaned not in valid:
            raise serializers.ValidationError('Storage condition must be one of: AMBIENT, REFRIGERATED, FROZEN, ROOM_TEMPERATURE.')
        return cleaned

    def validate(self, attrs):
        donation_id = attrs.get('donation_id')
        if donation_id is not None:
            donation = FoodDonation.objects.filter(id=donation_id).first()
            if donation is None:
                raise serializers.ValidationError({'donation_id': 'Donation was not found.'})
            attrs['donation'] = donation
        return attrs
