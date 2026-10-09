from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = (
            'id', 'title', 'message', 'event_code', 'action_url',
            'notification_type', 'is_read', 'related_donation_id', 'created_at',
        )
        read_only_fields = fields
