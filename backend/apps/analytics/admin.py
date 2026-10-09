from django.contrib import admin

from .models import ImpactMetric


@admin.register(ImpactMetric)
class ImpactMetricAdmin(admin.ModelAdmin):
    list_display = ('report_date', 'ngo', 'meals_distributed', 'kg_rescued_display', 'waste_avoided_kg')
    list_filter = ('report_date',)

    def kg_rescued_display(self, obj):
        return obj.kilograms_rescued

    kg_rescued_display.short_description = 'Kg rescued'
