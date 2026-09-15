import base64
import os

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_SYSTEM_ADMIN = "system_admin"
    ROLE_NATIONAL_MANAGER = "national_manager"
    ROLE_UNION_FOCAL = "union_focal"
    ROLE_DATA_COLLECTOR = "data_collector"
    ROLE_READ_ONLY = "read_only"

    ROLE_CHOICES = [
        (ROLE_SYSTEM_ADMIN, "System Admin"),
        (ROLE_NATIONAL_MANAGER, "National Project Manager"),
        (ROLE_UNION_FOCAL, "Trade Union Focal Person"),
        (ROLE_DATA_COLLECTOR, "Data Collector"),
        (ROLE_READ_ONLY, "Read-Only"),
    ]

    role = models.CharField(max_length=32, choices=ROLE_CHOICES, default=ROLE_READ_ONLY)
    phone = models.CharField(max_length=40, blank=True)
    organisation = models.CharField(max_length=160, blank=True)
    assigned_union = models.CharField(
        max_length=160,
        blank=True,
        help_text="Restricts focal-person and collector views to this union when set.",
    )
    totp_enabled = models.BooleanField(default=False)
    totp_secret = models.CharField(max_length=64, blank=True)

    def save(self, *args, **kwargs):
        if self.totp_enabled and not self.totp_secret:
            self.totp_secret = base64.b32encode(os.urandom(20)).decode("utf-8").rstrip("=")
        super().save(*args, **kwargs)

    @property
    def is_system_admin(self) -> bool:
        return self.is_superuser or self.role == self.ROLE_SYSTEM_ADMIN

    @property
    def can_edit_records(self) -> bool:
        return self.is_system_admin or self.role in {
            self.ROLE_NATIONAL_MANAGER,
            self.ROLE_UNION_FOCAL,
            self.ROLE_DATA_COLLECTOR,
        }


class UserCategory(models.Model):
    role = models.CharField(max_length=32, choices=User.ROLE_CHOICES, unique=True)
    display_name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "display_name"]
        verbose_name = "User category / role setting"
        verbose_name_plural = "User categories / role settings"

    def __str__(self) -> str:
        return self.display_name
