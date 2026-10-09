from django.contrib import admin

from .models import AuditLog, FraudAlert


@admin.register(FraudAlert)
class FraudAlertAdmin(admin.ModelAdmin):
    list_display = ('alert_type', 'actor', 'risk_score', 'severity', 'status', 'last_seen_at')
    list_filter = ('severity', 'status', 'detection_method')
    readonly_fields = ('actor', 'donation', 'alert_type', 'severity', 'risk_score', 'reason', 'reasons', 'deduplication_key', 'detection_method', 'rule_version', 'occurrence_count', 'status', 'created_at', 'updated_at', 'last_seen_at', 'reviewed_by', 'reviewed_at', 'review_outcome', 'review_note')
    search_fields = ('actor__username', 'reason', 'donation__food_name')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'entity_type', 'entity_id', 'actor', 'created_at')
    list_filter = ('action', 'entity_type')
    readonly_fields = ('actor', 'entity_type', 'entity_id', 'action', 'message', 'created_at')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
