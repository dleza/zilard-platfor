from django.contrib import admin

from .models import StakeholderFeedback


@admin.register(StakeholderFeedback)
class StakeholderFeedbackAdmin(admin.ModelAdmin):
    list_display = ("created_at", "contact_name", "role_or_group", "page_url", "status")
    list_filter = ("status", "created_at", "role_or_group")
    search_fields = ("contact_name", "contact_email", "comment", "page_url", "role_or_group")
    readonly_fields = ("created_at", "updated_at")
