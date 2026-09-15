from django.db import models
from django.core.exceptions import ValidationError

from core.models import TimeStampedModel
from workers.choices import GROUPED_DISTRICT_CHOICES, PROVINCE_CHOICES, PROVINCE_DISTRICTS
from workers.models import Worker


class ProjectActivity(TimeStampedModel):
    ACTIVITY_TRAINING = "training"
    ACTIVITY_WORKSHOP = "workshop"
    ACTIVITY_AUDIT = "audit"
    ACTIVITY_EMPLOYER_ENGAGEMENT = "employer_engagement"
    ACTIVITY_ADVOCACY = "advocacy"
    ACTIVITY_ORGANISING = "organising"

    ACTIVITY_TYPE_CHOICES = [
        (ACTIVITY_TRAINING, "Training"),
        (ACTIVITY_WORKSHOP, "Workshop"),
        (ACTIVITY_AUDIT, "Accessibility audit"),
        (ACTIVITY_EMPLOYER_ENGAGEMENT, "Employer engagement"),
        (ACTIVITY_ADVOCACY, "Advocacy intervention"),
        (ACTIVITY_ORGANISING, "Organising activity"),
    ]

    title = models.CharField(max_length=220)
    activity_type = models.CharField(max_length=40, choices=ACTIVITY_TYPE_CHOICES)
    partner = models.CharField(max_length=160, blank=True)
    province = models.CharField(max_length=40, choices=PROVINCE_CHOICES)
    district = models.CharField(max_length=80, choices=GROUPED_DISTRICT_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    participants_total = models.PositiveIntegerField(default=0)
    participants_with_disabilities = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-start_date", "title"]
        verbose_name_plural = "Project activities"

    def __str__(self) -> str:
        return self.title

    def clean(self):
        super().clean()
        if self.province and self.district and self.district not in PROVINCE_DISTRICTS.get(self.province, []):
            raise ValidationError({"district": "Select a district that belongs to the selected province."})


class TrainingAttendance(TimeStampedModel):
    ROLE_PARTICIPANT = "participant"
    ROLE_FACILITATOR = "facilitator"
    ROLE_OBSERVER = "observer"

    ROLE_CHOICES = [
        (ROLE_PARTICIPANT, "Participant"),
        (ROLE_FACILITATOR, "Facilitator"),
        (ROLE_OBSERVER, "Observer"),
    ]

    activity = models.ForeignKey(ProjectActivity, on_delete=models.CASCADE, related_name="attendance")
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name="training_attendance")
    role = models.CharField(max_length=40, choices=ROLE_CHOICES, default=ROLE_PARTICIPANT)
    attended = models.BooleanField(default=True)
    certificate_issued = models.BooleanField(default=False)

    class Meta:
        unique_together = ("activity", "worker")
        ordering = ["activity", "worker__last_name"]

    def __str__(self) -> str:
        return f"{self.worker.full_name} - {self.activity.title}"
