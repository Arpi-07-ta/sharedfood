from django.contrib import admin

from .models import MatchAudit, MatchCandidate, NGORecommendation, NGOMatchingProfile


@admin.register(NGOMatchingProfile)
class NGOMatchingProfileAdmin(admin.ModelAdmin):
    list_display = ('ngo', 'capacity_kg', 'current_demand_score', 'reliability_score', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('ngo__username', 'ngo__ngo_profile__organization_name')


@admin.register(NGORecommendation)
class NGORecommendationAdmin(admin.ModelAdmin):
    list_display = ('donation', 'ngo', 'match_score', 'status', 'distance_km', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('donation__food_name', 'ngo__username', 'ngo__ngo_profile__organization_name')


@admin.register(MatchCandidate)
class MatchCandidateAdmin(admin.ModelAdmin):
    list_display = ('donation', 'request', 'compatibility_score', 'created_at')
    list_filter = ('created_at',)


@admin.register(MatchAudit)
class MatchAuditAdmin(admin.ModelAdmin):
    list_display = ('donation', 'request', 'decision', 'reviewer')
    list_filter = ('decision',)
