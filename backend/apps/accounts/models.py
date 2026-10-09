from django.contrib.auth.models import AbstractUser
from django.db import models

from .storage import PrivateUploadStorage


class User(AbstractUser):
    class Role(models.TextChoices):
        USER = 'USER', 'User'
        DONOR = 'DONOR', 'Donor'
        NGO = 'NGO', 'NGO'
        VOLUNTEER = 'VOLUNTEER', 'Volunteer'
        ADMIN = 'ADMIN', 'Admin'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.USER)
    phone_number = models.CharField(max_length=30, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accounts_user'
        indexes = [models.Index(fields=['role']), models.Index(fields=['email'])]

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.role})'


class DonorProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='donor_profile',
        limit_choices_to={'role': User.Role.DONOR},
    )
    organization_name = models.CharField(max_length=255, blank=True, default='')
    address = models.TextField(blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')
    state = models.CharField(max_length=100, blank=True, default='')
    country = models.CharField(max_length=100, blank=True, default='')
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accounts_donor_profile'

    def __str__(self):
        return f'{self.user} donor profile'


class NGOProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='ngo_profile',
        limit_choices_to={'role': User.Role.NGO},
    )
    organization_name = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=120, blank=True, default='')
    mission = models.TextField(blank=True, default='')
    address = models.TextField(blank=True, default='')
    contact_email = models.EmailField(blank=True, default='')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    city = models.CharField(max_length=100, blank=True, default='')
    state = models.CharField(max_length=100, blank=True, default='')
    country = models.CharField(max_length=100, blank=True, default='')
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accounts_ngo_profile'

    def __str__(self):
        return self.organization_name or str(self.user)


class VolunteerProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='volunteer_profile',
        limit_choices_to={'role': User.Role.VOLUNTEER},
    )
    skills = models.TextField(blank=True, default='')
    availability = models.CharField(max_length=255, blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')
    state = models.CharField(max_length=100, blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accounts_volunteer_profile'

    def __str__(self):
        return f'{self.user} volunteer profile'


class NGOVerification(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        SUSPENDED = 'SUSPENDED', 'Suspended'

    ngo = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='ngo_verification',
        limit_choices_to={'role': User.Role.NGO},
    )
    organization_name = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=120)
    documents_url = models.URLField(blank=True, default='')
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_ngos',
        limit_choices_to={'role': User.Role.ADMIN},
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    document = models.FileField(
        upload_to='ngo-verification/',
        storage=PrivateUploadStorage(),
        blank=True,
        null=True,
    )
    review_note = models.TextField(blank=True, default='')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accounts_ngo_verification'
        indexes = [models.Index(fields=['status'])]

    def __str__(self):
        return f'{self.organization_name} verification'
