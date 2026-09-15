from django.contrib import admin

from .models import (
    AccessibilityAudit,
    DisabilityProfile,
    LabourRightsRecord,
    Occupation,
    TradeUnion,
    Worker,
    WorkerDocument,
    Workplace,
)
from .forms import WorkerBaseForm, WorkplaceAdminForm


class DisabilityProfileInline(admin.StackedInline):
    model = DisabilityProfile
    extra = 0
    fieldsets = (
        (None, {"fields": ("disability_type", "other_disability_type", "severity")}),
        (
            "Support needs",
            {"fields": ("assistive_devices", "accommodation_requirements", "accessibility_challenges", "functional_limitations")},
        ),
        (
            "Washington Group inspired questions",
            {
                "fields": (
                    "wg_seeing",
                    "wg_hearing",
                    "wg_walking",
                    "wg_remembering",
                    "wg_self_care",
                    "wg_communicating",
                )
            },
        ),
    )


class LabourRightsInline(admin.StackedInline):
    model = LabourRightsRecord
    extra = 0


class WorkerDocumentInline(admin.TabularInline):
    model = WorkerDocument
    extra = 0
    readonly_fields = ("created_at", "updated_at")


@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    form = WorkerBaseForm
    list_display = (
        "unique_id",
        "full_name",
        "gender",
        "province",
        "district",
        "union_membership_status",
        "union_name",
        "capture_source",
        "capture_mode",
        "created_by",
        "data_verified",
    )
    list_filter = (
        "gender",
        "province",
        "employment_status",
        "union_membership_status",
        "capture_source",
        "capture_mode",
        "data_verified",
    )
    search_fields = ("unique_id", "first_name", "last_name", "other_names", "phone", "union_name", "district")
    readonly_fields = (
        "unique_id",
        "capture_source",
        "capture_mode",
        "captured_at_device",
        "created_by",
        "updated_by",
        "created_at",
        "updated_at",
        "verified_at",
    )
    inlines = [DisabilityProfileInline, LabourRightsInline, WorkerDocumentInline]


@admin.register(Occupation)
class OccupationAdmin(admin.ModelAdmin):
    list_display = ("name", "sector", "is_active", "sort_order", "updated_at")
    list_filter = ("is_active", "sector")
    search_fields = ("name", "description")
    list_editable = ("is_active", "sort_order")
    ordering = ("sort_order", "name")


@admin.register(TradeUnion)
class TradeUnionAdmin(admin.ModelAdmin):
    list_display = ("name", "full_name", "is_active", "sort_order", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("name", "full_name", "description")
    list_editable = ("is_active", "sort_order")
    ordering = ("sort_order", "name")


class AccessibilityAuditInline(admin.TabularInline):
    model = AccessibilityAudit
    extra = 0


@admin.register(Workplace)
class WorkplaceAdmin(admin.ModelAdmin):
    form = WorkplaceAdminForm
    list_display = ("employer_name", "workplace_name", "province", "district", "sector", "accessibility_status")
    list_filter = ("province", "sector", "accessibility_status", "union_presence")
    search_fields = ("employer_name", "workplace_name", "district", "address")
    inlines = [AccessibilityAuditInline]


@admin.register(DisabilityProfile)
class DisabilityProfileAdmin(admin.ModelAdmin):
    list_display = ("worker", "disability_type", "severity")
    list_filter = ("disability_type", "severity")
    search_fields = ("worker__first_name", "worker__last_name", "worker__unique_id")


@admin.register(WorkerDocument)
class WorkerDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "worker", "document_type", "uploaded_by", "created_at")
    list_filter = ("document_type", "created_at")
    search_fields = ("title", "worker__first_name", "worker__last_name", "worker__unique_id")


@admin.register(LabourRightsRecord)
class LabourRightsRecordAdmin(admin.ModelAdmin):
    list_display = ("worker", "grievance_reported", "case_status", "legal_support_provided")
    list_filter = ("grievance_reported", "case_status", "legal_support_provided")


@admin.register(AccessibilityAudit)
class AccessibilityAuditAdmin(admin.ModelAdmin):
    list_display = ("workplace", "audit_date", "auditor_name", "average_score")
    list_filter = ("audit_date",)
    search_fields = ("workplace__employer_name", "auditor_name", "findings")
