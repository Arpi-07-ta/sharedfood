from django.utils import timezone
from rest_framework import serializers

from apps.accounts.serializers import UserSerializer
from .models import DonationRequest, DonationStatusHistory, FoodCategory, FoodDonation
from .services import can_edit_donation, transition_donation_status


class FoodCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodCategory
        fields = ('id', 'name', 'slug', 'description')


class DonationStatusHistorySerializer(serializers.ModelSerializer):
    changed_by = UserSerializer(read_only=True)

    class Meta:
        model = DonationStatusHistory
        fields = ('id', 'previous_status', 'new_status', 'changed_by', 'note', 'created_at')


class DonationRequestSerializer(serializers.ModelSerializer):
    ngo_name = serializers.CharField(source='ngo.ngo_profile.organization_name', read_only=True)
    donation_name = serializers.CharField(source='donation.food_name', read_only=True)
    donation_category = serializers.CharField(source='donation.category.name', read_only=True)
    donor_name = serializers.CharField(source='donation.donor.get_full_name', read_only=True)

    class Meta:
        model = DonationRequest
        fields = ('id', 'donation_id', 'donation_name', 'donation_category', 'donor_name', 'ngo_name', 'requested_quantity', 'message', 'status', 'created_at', 'updated_at')
        read_only_fields = fields


class DonationRequestCreateSerializer(serializers.Serializer):
    requested_quantity = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    message = serializers.CharField(required=False, allow_blank=True, max_length=3000)

    def validate_requested_quantity(self, value):
        donation = self.context['donation']
        if value != donation.quantity:
            raise serializers.ValidationError('Partial allocations are not supported; request the full donation quantity.')
        return value


class FoodDonationSerializer(serializers.ModelSerializer):
    donor = UserSerializer(read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=FoodCategory.objects.all())
    image = serializers.ImageField(required=False, allow_null=True)
    status_history = DonationStatusHistorySerializer(many=True, read_only=True)
    ai_waste_prediction = serializers.SerializerMethodField()
    ai_urgency = serializers.SerializerMethodField()

    class Meta:
        model = FoodDonation
        fields = (
            'id',
            'donor',
            'food_name',
            'category',
            'description',
            'quantity',
            'unit',
            'preparation_time',
            'expiry_time',
            'storage_condition',
            'pickup_address',
            'latitude',
            'longitude',
            'image',
            'status',
            'created_at',
            'updated_at',
            'status_history',
            'ai_waste_prediction',
            'ai_urgency',
        )
        read_only_fields = ('id', 'donor', 'created_at', 'updated_at', 'status_history', 'ai_waste_prediction', 'ai_urgency')

    def get_ai_waste_prediction(self, obj):
        prediction = getattr(obj, 'waste_prediction', None)
        if not prediction:
            return None
        return {
            'risk_label': prediction.risk_label,
            'risk_probability': float(prediction.risk_probability),
            'predicted_waste_kg': float(prediction.predicted_waste_kg),
            'model_version': prediction.model_version,
            'model_status': 'prototype' if prediction.is_prototype else 'production',
        }

    def get_ai_urgency(self, obj):
        recommendation = obj.ai_recommendations.filter(recommendation_type='URGENT_DONATION').order_by('-created_at').first()
        if not recommendation:
            return None
        return {
            'urgency_level': recommendation.urgency_level,
            'score': float(recommendation.score),
            'explanation': recommendation.explanation,
        }

    def validate_quantity(self, value):
        if value is None or value <= 0:
            raise serializers.ValidationError('Quantity must be greater than zero.')
        return value

    def validate_expiry_time(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError('Donation expiry time must be in the future.')
        return value

    def validate(self, attrs):
        preparation_time = attrs.get('preparation_time', getattr(self.instance, 'preparation_time', None))
        expiry_time = attrs.get('expiry_time', getattr(self.instance, 'expiry_time', None))

        if preparation_time and expiry_time and preparation_time > expiry_time:
            raise serializers.ValidationError({'preparation_time': 'Preparation time cannot be later than the expiry time.'})

        if self.instance and not can_edit_donation(self.instance):
            raise serializers.ValidationError({'detail': 'This donation can no longer be edited.'})

        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        donation = FoodDonation.objects.create(
            donor=request.user,
            **validated_data,
        )
        if donation.status == FoodDonation.DonationStatus.AVAILABLE and donation.expiry_time <= timezone.now():
            raise serializers.ValidationError({'expiry_time': 'Donation expiry time must be in the future.'})
        return donation

    def update(self, instance, validated_data):
        request = self.context.get('request')
        target_status = validated_data.get('status')

        if not self.instance or not can_edit_donation(self.instance):
            raise serializers.ValidationError({'detail': 'This donation can no longer be edited.'})

        for field, value in validated_data.items():
            if field == 'status':
                continue
            setattr(instance, field, value)

        instance.save()

        if target_status is not None and target_status != instance.status:
            try:
                transition_donation_status(instance, target_status, actor=request.user if request else None, note='Status updated through API.')
            except Exception as exc:  # pragma: no cover - handled by DRF error conversion
                raise serializers.ValidationError(exc.detail if hasattr(exc, 'detail') else {'status': str(exc)})

        return instance
