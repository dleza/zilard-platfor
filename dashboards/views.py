import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.db.models import Count
from django.views.generic import TemplateView

from monitoring.models import ProjectActivity
from users.permissions import filter_workers_for_user
from workers.choices import DISABILITY_TYPE_CHOICES, GENDER_CHOICES, PROVINCE_CHOICES
from workers.models import Worker, Workplace


def _labelled_counts(queryset, field_name: str, choices) -> list[dict]:
    labels = dict(choices)
    rows = queryset.values(field_name).annotate(total=Count("id")).order_by(field_name)
    return [{"label": labels.get(row[field_name], row[field_name] or "Not recorded"), "value": row["total"]} for row in rows]


class DashboardHomeView(LoginRequiredMixin, TemplateView):
    template_name = "dashboards/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        workers = filter_workers_for_user(
            Worker.objects.select_related("disability_profile", "workplace"),
            self.request.user,
        )
        total_workers = workers.count()
        union_members = workers.filter(union_membership_status="member").count()
        verified_workers = workers.filter(data_verified=True).count()

        disability_breakdown = _labelled_counts(workers, "disability_profile__disability_type", DISABILITY_TYPE_CHOICES)
        gender_distribution = _labelled_counts(workers, "gender", GENDER_CHOICES)
        province_counts = [
            {"label": province, "value": workers.filter(province=province).count()}
            for province, _label in PROVINCE_CHOICES
        ]
        union_counts = list(
            workers.exclude(union_name="")
            .values("union_name")
            .annotate(total=Count("id"))
            .order_by("-total", "union_name")[:8]
        )
        accessibility_counts = list(
            Workplace.objects.values("accessibility_status").annotate(total=Count("id")).order_by("accessibility_status")
        )

        markers = [
            {
                "id": worker.id,
                "name": worker.full_name,
                "unique_id": worker.unique_id,
                "province": worker.province,
                "district": worker.district,
                "lat": float(worker.latitude),
                "lng": float(worker.longitude),
                "url": reverse("workers:detail", args=[worker.pk]),
                "capture_source": worker.get_capture_source_display(),
                "capture_mode": worker.get_capture_mode_display(),
            }
            for worker in workers.exclude(latitude__isnull=True).exclude(longitude__isnull=True)[:250]
        ]

        context.update(
            {
                "total_workers": total_workers,
                "union_members": union_members,
                "verified_workers": verified_workers,
                "workplaces_total": Workplace.objects.count(),
                "activities_total": ProjectActivity.objects.count(),
                "disability_breakdown_json": json.dumps(disability_breakdown),
                "gender_distribution_json": json.dumps(gender_distribution),
                "province_counts_json": json.dumps(province_counts),
                "union_counts_json": json.dumps(
                    [{"label": row["union_name"], "value": row["total"]} for row in union_counts]
                ),
                "accessibility_counts_json": json.dumps(
                    [{"label": row["accessibility_status"].replace("_", " ").title(), "value": row["total"]} for row in accessibility_counts]
                ),
                "map_markers_json": json.dumps(markers),
            }
        )
        return context


class WorkerMapView(LoginRequiredMixin, TemplateView):
    template_name = "dashboards/map.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        workers = filter_workers_for_user(Worker.objects.all(), self.request.user)
        markers = [
            {
                "id": worker.id,
                "name": worker.full_name,
                "unique_id": worker.unique_id,
                "province": worker.province,
                "district": worker.district,
                "lat": float(worker.latitude),
                "lng": float(worker.longitude),
                "url": reverse("workers:detail", args=[worker.pk]),
                "capture_source": worker.get_capture_source_display(),
                "capture_mode": worker.get_capture_mode_display(),
            }
            for worker in workers.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
        ]
        context["map_markers_json"] = json.dumps(markers)
        return context
