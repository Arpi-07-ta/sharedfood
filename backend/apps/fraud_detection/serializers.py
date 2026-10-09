from rest_framework import serializers

from .models import FraudAlert


class FraudAlertSerializer(serializers.ModelSerializer):
    actor_username = serializers.SerializerMethodField()
    donation_name = serializers.SerializerMethodField()
    risk_level = serializers.CharField(source='severity', read_only=True)

    class Meta:
        model = FraudAlert
        fields = (
            'id',
            'actor_id',
            'actor_username',
            'donation_id',
            'donation_name',
            'alert_type',
            'risk_score',
            'risk_level',
            'reason',
            'reasons',
            'detection_method',
            'rule_version',
            'occurrence_count',
            'status',
            'review_outcome',
            'review_note',
            'reviewed_by_id',
            'reviewed_at',
            'created_at',
            'updated_at',
            'last_seen_at',
        )
        read_only_fields = fields

    def get_actor_username(self, obj):
        return obj.actor.username if obj.actor_id else '[deleted account]'

    def get_donation_name(self, obj):
        return obj.donation.food_name if obj.donation_id else None


class FraudAlertReviewSerializer(serializers.Serializer):
    outcome = serializers.ChoiceField(choices=FraudAlert.ReviewOutcome.choices)
    note = serializers.CharField(required=False, allow_blank=True, max_length=5000)
