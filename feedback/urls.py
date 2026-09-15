from django.urls import path

from .views import FeedbackCreateView, FeedbackListView

app_name = "feedback"

urlpatterns = [
    path("", FeedbackListView.as_view(), name="list"),
    path("submit/", FeedbackCreateView.as_view(), name="submit"),
]
