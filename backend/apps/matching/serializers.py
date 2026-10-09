from rest_framework import serializers

from apps.donations.models import FoodCategory

from .models import NGORecommendation, NGOMatchingProfile


class NGOMatchingProfileSerializer(serializers.ModelSerializer):
    accepted_categories = serializers.PrimaryKeyRelatedField(
        queryset=FoodCategory.objects.all(),
        many=True,
        required=False,
    )

    class Meta:
        model = NGOMatchingProfile
        fields = (
            'accepted_categories',
            'latitude',
            'longitude',
            'capacity_kg',
            'current_demand_score',
            'reliability_score',
            'is_active',
            'updated_at',
        )
        read_only_fields = ('reliability_score', 'is_active', 'updated_at')
        extra_kwargs = {
            'latitude': {'required': False, 'allow_null': True, 'min_value': -90, 'max_value': 90},
            'longitude': {'required': False, 'allow_null': True, 'min_value': -180, 'max_value': 180},
            'capacity_kg': {'required': False, 'min_value': 0},
            'current_demand_score': {'required': False, 'min_value': 0, 'max_value': 100},
        }

    def validate(self, attrs):
        instance = self.instance
        latitude = attrs.get('latitude', instance.latitude if instance else None)
        longitude = attrs.get('longitude', instance.longitude if instance else None)
        if (latitude is None) != (longitude is None):
            raise serializers.ValidationError('Provide both latitude and longitude, or leave both blank.')
        return attrs


class NGORecommendationSerializer(serializers.ModelSerializer):
    donation_id = serializers.IntegerField(read_only=True)
    donation_food_name = serializers.CharField(source='donation.food_name', read_only=True)
    donation_category = serializers.CharField(source='donation.category.name', read_only=True)
    donation_quantity = serializers.DecimalField(source='donation.quantity', max_digits=10, decimal_places=2, read_only=True)
    donation_unit = serializers.CharField(source='donation.unit', read_only=True)
    ngo_id = serializers.IntegerField(read_only=True)
    ngo_name = serializers.CharField(source='ngo.ngo_profile.organization_name', read_only=True)
    compatibility_score = serializers.SerializerMethodField()

    class Meta:
        model = NGORecommendation
        fields = (
            'id',
            'donation_id',
            'donation_food_name',
            'donation_category',
            'donation_quantity',
            'donation_unit',
            'ngo_id',
            'ngo_name',
            'match_score',
            'compatibility_score',
            'distance_km',
            'factor_scores',
            'factor_weights',
            'explanation',
            'status',
            'created_at',
            'accepted_at',
        )
        read_only_fields = fields

    def get_compatibility_score(self, obj):
        return obj.factor_scores.get('food_compatibility')
