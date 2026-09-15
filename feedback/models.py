from django.conf import settings
from django.db import models

from core.models import TimeStampedModel


class StakeholderFeedback(TimeStampedModel):
    STATUS_NEW = "new"
    STATUS_REVIEWED = "reviewed"
    STATUS_PLANNED = "planned"
    STATUS_CLOSED = "closed"

    STATUS_CHOICES = [
        (STATUS_NEW, "New"),
        (STATUS_REVIEWED, "Reviewed"),
        (STATUS_PLANNED, "Planned"),
        (STATUS_CLOSED, "Closed"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="feedback_items",
    )
    contact_name = models.CharField(max_length=160, blank=True)
    contact_email = models.EmailField(blank=True)
    role_or_group = models.CharField(max_length=160, blank=True)
    page_url = models.CharField(max_length=500, blank=True)
    comment = models.TextField()
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=STATUS_NEW)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Feedback from {self.contact_name or self.user or 'Stakeholder'}"
