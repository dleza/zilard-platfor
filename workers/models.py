import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from core.models import TimeStampedModel

from .choices import (
    ACCESSIBILITY_STATUS_CHOICES,
    DISABILITY_TYPE_CHOICES,
    EMPLOYMENT_STATUS_CHOICES,
    GENDER_CHOICES,
    GROUPED_DISTRICT_CHOICES,
    PROVINCE_CHOICES,
    PROVINCE_DISTRICTS,
    SECTOR_CHOICES,
    SEVERITY_CHOICES,
    UNION_MEMBERSHIP_CHOICES,
    WASHINGTON_GROUP_CHOICES,
)


def generate_worker_id() -> str:
    return f"DLDMS-{uuid.uuid4().hex[:8].upper()}"


def worker_photo_path(instance, filename: str) -> str:
    return f"workers/{instance.unique_id}/photos/{filename}"


def worker_document_path(instance, filename: str) -> str:
    return f"workers/{instance.worker.unique_id}/documents/{filename}"


def audit_document_path(instance, filename: str) -> str:
    return f"workplaces/{instance.workplace_id}/audits/{filename}"


class Workplace(TimeStampedModel):
    employer_name = models.CharField(max_length=180)
    workplace_name = models.CharField(max_length=180, blank=True)
    province = models.CharField(max_length=40, choices=PROVINCE_CHOICES)
    district = models.CharField(max_length=80, choices=GROUPED_DISTRICT_CHOICES)
    address = models.CharField(max_length=255, blank=True)
    sector = models.CharField(max_length=60, choices=SECTOR_CHOICES)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    accessibility_status = models.CharField(
        max_length=40,
        choices=ACCESSIBILITY_STATUS_CHOICES,
        default="not_assessed",
    )
    accommodations_available = models.BooleanField(default=False)
    union_presence = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["employer_name", "district"]

    def __str__(self) -> str:
        label = self.workplace_name or self.employer_name
        return f"{label} - {self.district}"

    def clean(self):
        super().clean()
        if self.province and self.district and self.district not in PROVINCE_DISTRICTS.get(self.province, []):
            raise ValidationError({"district": "Select a district that belongs to the selected province."})


class AccessibilityAudit(TimeStampedModel):
    workplace = models.ForeignKey(Workplace, on_delete=models.CASCADE, related_name="audits")
    audit_date = models.DateField(default=timezone.localdate)
    auditor_name = models.CharField(max_length=160)
    entrance_score = models.PositiveSmallIntegerField(default=0)
    restroom_score = models.PositiveSmallIntegerField(default=0)
    workstation_score = models.PositiveSmallIntegerField(default=0)
    transport_score = models.PositiveSmallIntegerField(default=0)
    findings = models.TextField()
    recommendations = models.TextField(blank=True)
    evidence_upload = models.FileField(upload_to=audit_document_path, blank=True)

    class Meta:
        ordering = ["-audit_date", "-created_at"]

    @property
    def average_score(self) -> float:
        return round(
            (self.entrance_score + self.restroom_score + self.workstation_score + self.transport_score) / 4,
            1,
        )

    def __str__(self) -> str:
        return f"Accessibility audit for {self.workplace} on {self.audit_date}"


class Occupation(TimeStampedModel):
    name = models.CharField(max_length=140, unique=True)
    sector = models.CharField(max_length=60, choices=SECTOR_CHOICES, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "Occupation setting"
        verbose_name_plural = "Occupation settings"

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.strip()
        super().save(*args, **kwargs)


class TradeUnion(TimeStampedModel):
    name = models.CharField(max_length=160, unique=True)
    full_name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "Trade union setting"
        verbose_name_plural = "Trade union settings"

    def __str__(self) -> str:
        return self.full_name or self.name

    def save(self, *args, **kwargs):
        self.name = self.name.strip()
        self.full_name = self.full_name.strip()
        super().save(*args, **kwargs)


class Worker(TimeStampedModel):
    CAPTURE_SOURCE_WEB = "web"
    CAPTURE_SOURCE_MOBILE = "mobile"
    CAPTURE_SOURCE_CHOICES = [
        (CAPTURE_SOURCE_WEB, "Web portal"),
        (CAPTURE_SOURCE_MOBILE, "Mobile app"),
    ]

    CAPTURE_MODE_ONLINE = "online"
    CAPTURE_MODE_OFFLINE = "offline"
    CAPTURE_MODE_CHOICES = [
        (CAPTURE_MODE_ONLINE, "Online"),
        (CAPTURE_MODE_OFFLINE, "Offline queued"),
    ]

    unique_id = models.CharField(max_length=32, unique=True, default=generate_worker_id, editable=False)
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    other_names = models.CharField(max_length=120, blank=True)
    national_id = models.CharField(max_length=80, blank=True)
    nationality = models.CharField(max_length=80, default="Zambian")
    gender = models.CharField(max_length=32, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=40, blank=True)
    email = models.EmailField(blank=True)
    province = models.CharField(max_length=40, choices=PROVINCE_CHOICES)
    district = models.CharField(max_length=80, choices=GROUPED_DISTRICT_CHOICES)
    workplace = models.ForeignKey(Workplace, null=True, blank=True, on_delete=models.SET_NULL, related_name="workers")
    sector = models.CharField(max_length=60, choices=SECTOR_CHOICES)
    occupation = models.CharField(max_length=140, blank=True)
    employment_status = models.CharField(max_length=40, choices=EMPLOYMENT_STATUS_CHOICES)
    union_membership_status = models.CharField(
        max_length=32,
        choices=UNION_MEMBERSHIP_CHOICES,
        default="unknown",
    )
    union_name = models.CharField(max_length=160, blank=True)
    leadership_participation = models.BooleanField(default=False)
    committee_participation = models.BooleanField(default=False)
    organising_activities = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    photo = models.ImageField(upload_to=worker_photo_path, blank=True)
    consent_to_store_data = models.BooleanField(default=True)
    data_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    capture_source = models.CharField(
        max_length=16,
        choices=CAPTURE_SOURCE_CHOICES,
        default=CAPTURE_SOURCE_WEB,
    )
    capture_mode = models.CharField(
        max_length=16,
        choices=CAPTURE_MODE_CHOICES,
        default=CAPTURE_MODE_ONLINE,
    )
    captured_at_device = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Original device timestamp for records first captured offline.",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="workers_created",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="workers_updated",
    )

    class Meta:
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(fields=["unique_id"]),
            models.Index(fields=["province", "district"]),
            models.Index(fields=["union_name"]),
            models.Index(fields=["capture_source", "capture_mode"]),
        ]

    @property
    def full_name(self) -> str:
        names = [self.first_name, self.other_names, self.last_name]
        return " ".join(part for part in names if part).strip()

    @property
    def age(self) -> int | None:
        if not self.date_of_birth:
            return None
        today = timezone.localdate()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    @property
    def captured_by_display(self) -> str:
        if not self.created_by:
            return "Not recorded"
        return self.created_by.get_full_name() or self.created_by.get_username()

    def __str__(self) -> str:
        return f"{self.unique_id} - {self.full_name}"

    def clean(self):
        super().clean()
        if self.province and self.district and self.district not in PROVINCE_DISTRICTS.get(self.province, []):
            raise ValidationError({"district": "Select a district that belongs to the selected province."})


class DisabilityProfile(TimeStampedModel):
    worker = models.OneToOneField(Worker, on_delete=models.CASCADE, related_name="disability_profile")
    disability_type = models.CharField(max_length=40, choices=DISABILITY_TYPE_CHOICES)
    other_disability_type = models.CharField(max_length=160, blank=True)
    severity = models.CharField(max_length=40, choices=SEVERITY_CHOICES)
    assistive_devices = models.TextField(blank=True)
    accommodation_requirements = models.TextField(blank=True)
    accessibility_challenges = models.TextField(blank=True)
    functional_limitations = models.TextField(blank=True)
    wg_seeing = models.PositiveSmallIntegerField(choices=WASHINGTON_GROUP_CHOICES, default=0)
    wg_hearing = models.PositiveSmallIntegerField(choices=WASHINGTON_GROUP_CHOICES, default=0)
    wg_walking = models.PositiveSmallIntegerField(choices=WASHINGTON_GROUP_CHOICES, default=0)
    wg_remembering = models.PositiveSmallIntegerField(choices=WASHINGTON_GROUP_CHOICES, default=0)
    wg_self_care = models.PositiveSmallIntegerField(choices=WASHINGTON_GROUP_CHOICES, default=0)
    wg_communicating = models.PositiveSmallIntegerField(choices=WASHINGTON_GROUP_CHOICES, default=0)

    class Meta:
        ordering = ["worker__last_name", "worker__first_name"]

    def __str__(self) -> str:
        return f"{self.worker.full_name} - {self.get_disability_type_display()}"


class WorkerDocument(TimeStampedModel):
    DOCUMENT_PHOTO = "photo"
    DOCUMENT_AUDIT = "audit"
    DOCUMENT_MEDICAL = "medical"
    DOCUMENT_CONSENT = "consent"
    DOCUMENT_OTHER = "other"

    DOCUMENT_TYPE_CHOICES = [
        (DOCUMENT_PHOTO, "Photo"),
        (DOCUMENT_AUDIT, "Audit evidence"),
        (DOCUMENT_MEDICAL, "Medical or assessment document"),
        (DOCUMENT_CONSENT, "Consent document"),
        (DOCUMENT_OTHER, "Other"),
    ]

    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name="documents")
    title = models.CharField(max_length=160)
    document_type = models.CharField(max_length=40, choices=DOCUMENT_TYPE_CHOICES, default=DOCUMENT_OTHER)
    file = models.FileField(upload_to=worker_document_path)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="worker_documents_uploaded",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.title} for {self.worker.full_name}"


class LabourRightsRecord(TimeStampedModel):
    CASE_OPEN = "open"
    CASE_RESOLVED = "resolved"
    CASE_REFERRED = "referred"
    CASE_MONITORING = "monitoring"
    CASE_NONE = "none"

    CASE_STATUS_CHOICES = [
        (CASE_NONE, "No active case"),
        (CASE_OPEN, "Open"),
        (CASE_MONITORING, "Monitoring"),
        (CASE_REFERRED, "Referred"),
        (CASE_RESOLVED, "Resolved"),
    ]

    worker = models.OneToOneField(Worker, on_delete=models.CASCADE, related_name="labour_rights")
    grievance_reported = models.BooleanField(default=False)
    grievance_summary = models.TextField(blank=True)
    case_status = models.CharField(max_length=32, choices=CASE_STATUS_CHOICES, default=CASE_NONE)
    legal_support_provided = models.BooleanField(default=False)
    collective_bargaining_coverage = models.BooleanField(default=False)
    social_protection_coverage = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Labour rights record"
        verbose_name_plural = "Labour rights records"

    def __str__(self) -> str:
        return f"Labour rights: {self.worker.full_name}"
