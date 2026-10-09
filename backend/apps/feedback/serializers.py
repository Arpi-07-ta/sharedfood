from rest_framework import serializers

from apps.donations.models import FoodDonation

from .models import Complaint, Feedback


class NGOFeedbackSerializer(serializers.ModelSerializer):
    sender_id = serializers.IntegerField(source='user_id', read_only=True)
    receiver_id = serializers.IntegerField(read_only=True)
    receiver_name = serializers.SerializerMethodField()

    class Meta:
        model = Feedback
        fields = ('id', 'donation', 'sender_id', 'receiver_id', 'receiver_name', 'category', 'rating', 'comment', 'created_at')
        read_only_fields = ('id', 'sender_id', 'receiver_id', 'receiver_name', 'created_at')
        extra_kwargs = {
            'donation': {'queryset': FoodDonation.objects.all()},
            'category': {'required': False},
            'comment': {'required': False},
        }

    def get_receiver_name(self, obj):
        return (obj.receiver.get_full_name() or obj.receiver.username) if obj.receiver_id else None


class ComplaintSerializer(serializers.ModelSerializer):
    submitted_by = serializers.SerializerMethodField()

    class Meta:
        model = Complaint
        fields = ('id', 'user_id', 'submitted_by', 'donation_id', 'title', 'description', 'status', 'review_note', 'reviewed_by_id', 'reviewed_at', 'created_at', 'updated_at')
        read_only_fields = fields

    def get_submitted_by(self, obj):
        return obj.user.get_full_name() or obj.user.username


class ComplaintCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = ('donation', 'title', 'description')
        extra_kwargs = {
            'donation': {'required': False, 'allow_null': True},
            'title': {'max_length': 255},
        }

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError('Complaint title cannot be blank.')
        return value.strip()

    def validate_description(self, value):
        if not value.strip():
            raise serializers.ValidationError('Complaint details cannot be blank.')
        return value.strip()


class ComplaintReviewSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=(Complaint.ComplaintStatus.REVIEWING, Complaint.ComplaintStatus.RESOLVED))
    note = serializers.CharField(required=False, allow_blank=True, max_length=5000)
