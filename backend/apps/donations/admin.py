from django.contrib import admin

from .models import DonationMatch, DonationRequest, DonationStatusHistory, FoodCategory, FoodDonation


@admin.register(FoodCategory)
class FoodCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)


@admin.register(FoodDonation)
class FoodDonationAdmin(admin.ModelAdmin):
    list_display = ('food_name', 'donor', 'status', 'expiry_time', 'quantity')
    list_filter = ('status', 'storage_condition', 'category')
    search_fields = ('food_name', 'pickup_address')


@admin.register(DonationStatusHistory)
class DonationStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('donation', 'previous_status', 'new_status', 'changed_by', 'created_at')
    list_filter = ('new_status', 'previous_status')
    search_fields = ('donation__food_name', 'note')


@admin.register(DonationRequest)
class DonationRequestAdmin(admin.ModelAdmin):
    list_display = ('donation', 'ngo', 'requested_quantity', 'status')
    list_filter = ('status',)


@admin.register(DonationMatch)
class DonationMatchAdmin(admin.ModelAdmin):
    list_display = ('donation', 'request', 'status', 'match_score')
    list_filter = ('status',)
