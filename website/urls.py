from django.urls import path

from . import views

app_name = "website"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("our-work/", views.OurWorkView.as_view(), name="our-work"),
    path("our-work/<slug:slug>/", views.ThematicAreaDetailView.as_view(), name="work-detail"),
    path("projects/<slug:slug>/", views.ProjectDetailView.as_view(), name="project-detail"),
    path("research/", views.ResearchLibraryView.as_view(), name="research"),
    path("research/publication/<slug:slug>/", views.PublicationDetailView.as_view(), name="publication-detail"),
    path("research/activity/<slug:slug>/", views.ResearchActivityDetailView.as_view(), name="research-activity-detail"),
    path("news/", views.NewsListView.as_view(), name="news"),
    path("news/<slug:slug>/", views.NewsDetailView.as_view(), name="news-detail"),
    path("contact/", views.ContactView.as_view(), name="contact"),
]
