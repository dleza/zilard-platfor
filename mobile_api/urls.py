from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    MobileDashboardSummaryView,
    MobileFeedbackViewSet,
    MobileLabourRightsViewSet,
    MobileLoginView,
    MobileLookupView,
    MobileMeView,
    MobileWorkerViewSet,
    MobileWorkplaceViewSet,
)

app_name = "mobile_api"

router = DefaultRouter()
router.register("workers", MobileWorkerViewSet, basename="mobile-workers")
router.register("workplaces", MobileWorkplaceViewSet, basename="mobile-workplaces")
router.register("labour-rights", MobileLabourRightsViewSet, basename="mobile-labour-rights")
router.register("feedback", MobileFeedbackViewSet, basename="mobile-feedback")

urlpatterns = [
    path("auth/login/", MobileLoginView.as_view(), name="login"),
    path("auth/me/", MobileMeView.as_view(), name="me"),
    path("lookups/", MobileLookupView.as_view(), name="lookups"),
    path("dashboard/", MobileDashboardSummaryView.as_view(), name="dashboard"),
    path("", include(router.urls)),
]
