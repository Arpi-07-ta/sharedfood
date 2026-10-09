from decimal import Decimal

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .models import NGOProfile, NGOVerification, User, VolunteerProfile


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    is_verified = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'role',
            'is_verified',
        )

    def get_role(self, obj):
        return obj.role.lower()

    def get_is_verified(self, obj):
        if obj.role == User.Role.NGO:
            ngo_profile = getattr(obj, 'ngo_profile', None)
            verification = getattr(obj, 'ngo_verification', None)
            return bool(
                obj.is_active
                and ngo_profile
                and ngo_profile.is_verified
                and verification
                and verification.status == NGOVerification.Status.APPROVED
            )
        if obj.role == User.Role.DONOR:
            donor_profile = getattr(obj, 'donor_profile', None)
            return bool(donor_profile and donor_profile.is_verified)
        return False


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.CharField(required=False, default=User.Role.USER)
    organization_name = serializers.CharField(required=False, allow_blank=True, max_length=255)
    registration_number = serializers.CharField(required=False, allow_blank=True, max_length=120)
    mission = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True, max_length=100)
    state = serializers.CharField(required=False, allow_blank=True, max_length=100)
    country = serializers.CharField(required=False, allow_blank=True, max_length=100)
    contact_email = serializers.EmailField(required=False, allow_blank=True)
    skills = serializers.CharField(required=False, allow_blank=True)
    availability = serializers.CharField(required=False, allow_blank=True)
    volunteer_city = serializers.CharField(required=False, allow_blank=True, max_length=100)
    volunteer_state = serializers.CharField(required=False, allow_blank=True, max_length=100)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'phone_number', 'role',
            'organization_name', 'registration_number', 'mission', 'address', 'city',
            'state', 'country', 'contact_email', 'password', 'confirm_password',
            'skills', 'availability', 'volunteer_city', 'volunteer_state',
        )

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('A user with that email already exists.')
        return value

    def validate_role(self, value):
        normalized = str(value).strip().upper()
        allowed_roles = {User.Role.USER, User.Role.DONOR, User.Role.NGO, User.Role.VOLUNTEER}
        if normalized not in allowed_roles:
            raise serializers.ValidationError('Unsupported role selected for public registration.')
        return normalized

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        role = attrs.get('role')

        if password != confirm_password:
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match.'})
        validate_password(password)

        if role == User.Role.ADMIN:
            raise serializers.ValidationError({'role': 'Public registration cannot create admin accounts.'})
        if role == User.Role.NGO:
            if not attrs.get('organization_name', '').strip():
                raise serializers.ValidationError({'organization_name': 'Organization name is required for NGO registration.'})
            if not attrs.get('registration_number', '').strip():
                raise serializers.ValidationError({'registration_number': 'Registration number is required for NGO registration.'})
        if role == User.Role.VOLUNTEER and not attrs.get('phone_number', '').strip():
            raise serializers.ValidationError({'phone_number': 'A contact phone is required for volunteers.'})

        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        role = validated_data.pop('role', User.Role.USER)
        ngo_data = {}
        volunteer_data = {}
        if role == User.Role.NGO:
            ngo_data = {
                field: validated_data.pop(field, '')
                for field in ('organization_name', 'registration_number', 'mission', 'address', 'city', 'state', 'country', 'contact_email')
            }
            for field in ('skills', 'availability', 'volunteer_city', 'volunteer_state'):
                validated_data.pop(field, None)
        else:
            for field in ('organization_name', 'registration_number', 'mission', 'address', 'city', 'state', 'country', 'contact_email'):
                validated_data.pop(field, None)
            if role == User.Role.VOLUNTEER:
                volunteer_data = {
                    'skills': validated_data.pop('skills', ''),
                    'availability': validated_data.pop('availability', ''),
                    'city': validated_data.pop('volunteer_city', ''),
                    'state': validated_data.pop('volunteer_state', ''),
                }
            else:
                for field in ('skills', 'availability', 'volunteer_city', 'volunteer_state'):
                    validated_data.pop(field, None)

        with transaction.atomic():
            user = User.objects.create_user(password=password, role=role, **validated_data)
            if role == User.Role.NGO:
                NGOProfile.objects.create(user=user, **ngo_data)
                NGOVerification.objects.create(
                    ngo=user,
                    organization_name=ngo_data['organization_name'],
                    registration_number=ngo_data['registration_number'],
                )
            elif role == User.Role.VOLUNTEER:
                VolunteerProfile.objects.create(user=user, **volunteer_data)
        return user


class NGOProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    phone_number = serializers.CharField(source='user.phone_number', read_only=True)

    class Meta:
        model = NGOProfile
        fields = (
            'user_id', 'organization_name', 'registration_number', 'mission', 'address',
            'city', 'state', 'country', 'contact_email', 'latitude', 'longitude',
            'is_verified', 'email', 'phone_number', 'updated_at',
        )
        read_only_fields = ('user_id', 'registration_number', 'is_verified', 'email', 'phone_number', 'updated_at')
        extra_kwargs = {
            'latitude': {'required': False, 'allow_null': True, 'min_value': Decimal('-90'), 'max_value': Decimal('90')},
            'longitude': {'required': False, 'allow_null': True, 'min_value': Decimal('-180'), 'max_value': Decimal('180')},
        }

    def validate(self, attrs):
        instance = self.instance
        latitude = attrs.get('latitude', instance.latitude if instance else None)
        longitude = attrs.get('longitude', instance.longitude if instance else None)
        if (latitude is None) != (longitude is None):
            raise serializers.ValidationError('Provide both latitude and longitude, or leave both blank.')
        return attrs


class VolunteerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = VolunteerProfile
        fields = ('skills', 'availability', 'city', 'state', 'is_active', 'updated_at')
        read_only_fields = ('is_active', 'updated_at')
        extra_kwargs = {
            'skills': {'required': False},
            'availability': {'required': False},
            'city': {'required': False},
            'state': {'required': False},
        }


class NGOVerificationStatusSerializer(serializers.ModelSerializer):
    document_name = serializers.SerializerMethodField()

    class Meta:
        model = NGOVerification
        fields = ('id', 'organization_name', 'registration_number', 'documents_url', 'document_name', 'status', 'review_note', 'reviewed_at', 'created_at', 'updated_at')
        read_only_fields = fields

    def get_document_name(self, obj):
        return obj.document.name.rsplit('/', 1)[-1] if obj.document else None


class NGOVerificationSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NGOVerification
        fields = ('documents_url', 'document')
        extra_kwargs = {
            'documents_url': {'required': False, 'allow_blank': True},
            'document': {'required': False, 'allow_null': True},
        }

    def validate_document(self, value):
        if value and value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError('Verification documents must be no larger than 5 MB.')
        if value and value.content_type not in {'application/pdf', 'image/jpeg', 'image/png'}:
            raise serializers.ValidationError('Upload a PDF, JPEG, or PNG verification document.')
        return value


class NGOVerificationReviewSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=(
        NGOVerification.Status.APPROVED,
        NGOVerification.Status.REJECTED,
        NGOVerification.Status.SUSPENDED,
    ))
    note = serializers.CharField(required=False, allow_blank=True, max_length=5000)

    def validate(self, attrs):
        if attrs['status'] in {NGOVerification.Status.REJECTED, NGOVerification.Status.SUSPENDED} and not attrs.get('note', '').strip():
            raise serializers.ValidationError({'note': 'A note is required when rejecting or suspending an NGO.'})
        return attrs


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = User.objects.filter(email__iexact=email).first()
        if user is None or not user.check_password(password):
            raise AuthenticationFailed('Invalid email or password.')
        if not user.is_active:
            raise AuthenticationFailed('This account is disabled.')

        attrs['user'] = user
        return attrs


class FoodShareTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = User.objects.filter(email__iexact=email).first()
        if user is None:
            raise AuthenticationFailed('Invalid email or password.')

        if not user.check_password(password):
            raise AuthenticationFailed('Invalid email or password.')

        if not user.is_active:
            raise AuthenticationFailed('This account is disabled.')

        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data,
        }


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone_number')
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'phone_number': {'required': False},
        }
