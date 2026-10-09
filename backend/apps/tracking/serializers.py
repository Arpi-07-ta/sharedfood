from rest_framework import serializers

from .models import DeliveryLog, Pickup, PickupStatusHistory


class PickupStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = PickupStatusHistory
        fields = ('id', 'previous_status', 'new_status', 'changed_by_name', 'note', 'created_at')

    def get_changed_by_name(self, obj):
        return obj.changed_by.get_full_name() or obj.changed_by.username if obj.changed_by else 'System'


class DeliveryLogSerializer(serializers.ModelSerializer):
    proof_available = serializers.SerializerMethodField()

    class Meta:
        model = DeliveryLog
        fields = ('id', 'delivered_at', 'condition', 'comment', 'proof_available')

    def get_proof_available(self, obj):
        return bool(obj.proof_file)


class PickupSerializer(serializers.ModelSerializer):
    donation_id = serializers.IntegerField(read_only=True)
    donation_name = serializers.CharField(source='donation.food_name', read_only=True)
    quantity = serializers.DecimalField(source='donation.quantity', max_digits=10, decimal_places=2, read_only=True)
    unit = serializers.CharField(source='donation.unit', read_only=True)
    ngo_name = serializers.CharField(source='ngo.ngo_profile.organization_name', read_only=True)
    pickup_address = serializers.CharField(source='donation.pickup_address', read_only=True)
    status_history = PickupStatusHistorySerializer(many=True, read_only=True)
    delivery_log = serializers.SerializerMethodField()

    class Meta:
        model = Pickup
        fields = (
            'id', 'donation_id', 'donation_name', 'quantity', 'unit', 'ngo_name',
            'pickup_address', 'status', 'pickup_window_start', 'pickup_window_end',
            'notes', 'received_at', 'accepted_at', 'picked_up_at', 'delivered_at', 'cancelled_at',
            'status_history', 'delivery_log', 'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'donation_id', 'donation_name', 'quantity', 'unit', 'ngo_name', 'pickup_address', 'status', 'received_at', 'created_at', 'updated_at')

    def get_delivery_log(self, obj):
        log = obj.delivery_logs.order_by('-delivered_at').first()
        return DeliveryLogSerializer(log).data if log else None


class PickupScheduleSerializer(serializers.Serializer):
    pickup_window_start = serializers.DateTimeField()
    pickup_window_end = serializers.DateTimeField()
    notes = serializers.CharField(required=False, allow_blank=True, max_length=3000)

    def validate(self, attrs):
        if attrs['pickup_window_end'] <= attrs['pickup_window_start']:
            raise serializers.ValidationError({'pickup_window_end': 'Pickup window end must be after the start.'})
        return attrs


class PickupStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=(
        Pickup.PickupStatus.IN_TRANSIT,
        Pickup.PickupStatus.PICKED_UP,
        Pickup.PickupStatus.DELIVERED,
        Pickup.PickupStatus.CANCELLED,
    ))
    note = serializers.CharField(required=False, allow_blank=True, max_length=3000)
    proof_file = serializers.FileField(required=False, allow_null=True)

    def validate_proof_file(self, value):
        if value and value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError('Delivery proof must be no larger than 10 MB.')
        if value and value.content_type not in {'application/pdf', 'image/jpeg', 'image/png'}:
            raise serializers.ValidationError('Upload delivery proof as PDF, JPEG, or PNG.')
        return value
