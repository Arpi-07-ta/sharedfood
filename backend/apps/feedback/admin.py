from django.contrib import admin

from .models import Complaint, Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'donation', 'rating', 'category', 'created_at')
    list_filter = ('category', 'rating')


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'donation', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('title', 'description')
