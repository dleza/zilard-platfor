from django.urls import path

from .views import DashboardHomeView, WorkerMapView

app_name = "dashboards"

urlpatterns = [
    path("", DashboardHomeView.as_view(), name="home"),
    path("map/", WorkerMapView.as_view(), name="map"),
]
