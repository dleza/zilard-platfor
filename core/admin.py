from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "actor", "action", "model_name", "object_label")
    list_filter = ("action", "model_name", "created_at")
    search_fields = ("actor__username", "actor__email", "object_label", "summary")
    readonly_fields = ("created_at",)
