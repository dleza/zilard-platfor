"""Top-level URL routing."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from workers.api import DisabilityProfileViewSet, WorkerViewSet, WorkplaceViewSet

router = DefaultRouter()
router.register("workers", WorkerViewSet, basename="api-workers")
router.register("disability-profiles", DisabilityProfileViewSet, basename="api-disability-profiles")
router.register("workplaces", WorkplaceViewSet, basename="api-workplaces")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("users.urls")),
    # Public ZILARD website -- owns the root URL.
    path("", include("website.urls")),
    # Internal Disability Labour Data MIS (login required) now lives under /app/.
    path("app/", include("dashboards.urls")),
    path("app/workers/", include("workers.urls")),
    path("app/reports/", include("reports.urls")),
    path("app/feedback/", include("feedback.urls")),
    path("api/mobile/", include("mobile_api.urls")),
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
