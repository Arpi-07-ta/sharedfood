from django.contrib import admin

from .models import DonorProfile, NGOProfile, NGOVerification, User, VolunteerProfile


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'email', 'phone_number')


@admin.register(DonorProfile)
class DonorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization_name', 'is_verified', 'city')
    list_filter = ('is_verified', 'city')


@admin.register(NGOProfile)
class NGOProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization_name', 'registration_number', 'is_verified', 'city')
    list_filter = ('is_verified', 'city')


@admin.register(VolunteerProfile)
class VolunteerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'is_active')
    list_filter = ('is_active', 'city')


@admin.register(NGOVerification)
class NGOVerificationAdmin(admin.ModelAdmin):
    list_display = ('ngo', 'organization_name', 'status', 'verified_by')
    list_filter = ('status',)
    search_fields = ('organization_name', 'registration_number')
