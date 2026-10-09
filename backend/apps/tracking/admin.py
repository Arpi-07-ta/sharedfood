from django.contrib import admin

from .models import Beneficiary, DeliveryLog, Pickup


@admin.register(Beneficiary)
class BeneficiaryAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'city', 'state')
    search_fields = ('name', 'phone_number')


@admin.register(Pickup)
class PickupAdmin(admin.ModelAdmin):
    list_display = ('donation', 'beneficiary', 'assigned_volunteer', 'status', 'pickup_window_start')
    list_filter = ('status',)


@admin.register(DeliveryLog)
class DeliveryLogAdmin(admin.ModelAdmin):
    list_display = ('pickup', 'delivered_by', 'delivered_at', 'condition')
    list_filter = ('condition',)
