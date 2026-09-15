from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, UserCategory


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (
            "DMIS access",
            {
                "fields": (
                    "role",
                    "phone",
                    "organisation",
                    "assigned_union",
                    "totp_enabled",
                    "totp_secret",
                )
            },
        ),
    )
    list_display = ("username", "email", "role", "organisation", "assigned_union", "is_staff")
    list_filter = ("role", "is_staff", "is_superuser", "totp_enabled")
    search_fields = ("username", "email", "first_name", "last_name", "organisation", "assigned_union")


@admin.register(UserCategory)
class UserCategoryAdmin(admin.ModelAdmin):
    list_display = ("display_name", "role", "is_active", "sort_order", "updated_at")
    list_filter = ("is_active", "role")
    search_fields = ("display_name", "description")
    list_editable = ("is_active", "sort_order")
    ordering = ("sort_order", "display_name")
