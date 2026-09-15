from django.contrib import admin

from .models import ProjectActivity, TrainingAttendance


class TrainingAttendanceInline(admin.TabularInline):
    model = TrainingAttendance
    extra = 0
    autocomplete_fields = ("worker",)


@admin.register(ProjectActivity)
class ProjectActivityAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "activity_type",
        "partner",
        "province",
        "district",
        "start_date",
        "participants_total",
        "participants_with_disabilities",
    )
    list_filter = ("activity_type", "partner", "province", "start_date")
    search_fields = ("title", "partner", "district", "notes")
    inlines = [TrainingAttendanceInline]


@admin.register(TrainingAttendance)
class TrainingAttendanceAdmin(admin.ModelAdmin):
    list_display = ("activity", "worker", "role", "attended", "certificate_issued")
    list_filter = ("role", "attended", "certificate_issued")
    search_fields = ("activity__title", "worker__first_name", "worker__last_name", "worker__unique_id")
    autocomplete_fields = ("activity", "worker")
