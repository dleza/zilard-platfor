from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, ListView, TemplateView

from .forms import ContactForm
from .models import (
    HomeSlide,
    NewsArticle,
    Partner,
    Project,
    Publication,
    ResearchActivity,
    SiteSetting,
    TeamMember,
    ThematicArea,
)


class HomeView(TemplateView):
    template_name = "website/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "slides": HomeSlide.objects.published().select_related("news_article")[:8],
                "themes": ThematicArea.objects.published()[:4],
                "featured_publications": Publication.objects.published().filter(is_featured=True)[:3]
                or Publication.objects.published()[:3],
                "projects": Project.objects.published().filter(status="ongoing")[:2]
                or Project.objects.published()[:2],
                "news_items": NewsArticle.objects.published()[:3],
                "partners": Partner.objects.published()[:8],
            }
        )
        return context


class AboutView(TemplateView):
    template_name = "website/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "team_leadership": TeamMember.objects.published().filter(group__in=["board", "management"]),
                "team_staff": TeamMember.objects.published().filter(group="staff"),
                "team_researchers": TeamMember.objects.published().filter(group="researcher"),
                "partners": Partner.objects.published(),
            }
        )
        return context


class OurWorkView(ListView):
    template_name = "website/our_work.html"
    context_object_name = "themes"
    queryset = ThematicArea.objects.published()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["projects"] = Project.objects.published()
        return context


class ThematicAreaDetailView(DetailView):
    template_name = "website/work_detail.html"
    context_object_name = "theme"
    queryset = ThematicArea.objects.published()
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        theme = self.object
        context["projects"] = theme.projects.filter(is_published=True)
        context["research_activities"] = theme.research_activities.filter(is_published=True)
        context["publications"] = theme.publications.filter(is_published=True)
        return context


class ProjectDetailView(DetailView):
    template_name = "website/project_detail.html"
    context_object_name = "project"
    queryset = Project.objects.published()
    slug_url_kwarg = "slug"


class ResearchLibraryView(TemplateView):
    template_name = "website/research.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        publications = Publication.objects.published()
        research_activities = ResearchActivity.objects.published()

        year = self.request.GET.get("year")
        theme_slug = self.request.GET.get("theme")
        query = self.request.GET.get("q")

        if year:
            publications = publications.filter(publication_date__year=year)
            research_activities = research_activities.filter(year=year)
        if theme_slug:
            publications = publications.filter(theme__slug=theme_slug)
            research_activities = research_activities.filter(theme__slug=theme_slug)
        if query:
            publications = publications.filter(title__icontains=query) | publications.filter(
                summary__icontains=query
            )

        publication_years = set(
            Publication.objects.published().values_list("publication_date__year", flat=True)
        )
        research_years = set(ResearchActivity.objects.published().values_list("year", flat=True))
        years = sorted(publication_years | research_years, reverse=True)

        context.update(
            {
                "publications": publications,
                "research_activities": research_activities,
                "themes": ThematicArea.objects.published(),
                "years": years,
                "current_year": year,
                "current_theme": theme_slug,
                "query": query or "",
            }
        )
        return context


class PublicationDetailView(DetailView):
    template_name = "website/publication_detail.html"
    context_object_name = "publication"
    queryset = Publication.objects.published()
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        publication = self.object
        related = Publication.objects.published().exclude(pk=publication.pk)
        if publication.theme_id:
            related = related.filter(theme=publication.theme)
        context["related_publications"] = related[:3]
        return context


class ResearchActivityDetailView(DetailView):
    template_name = "website/research_activity_detail.html"
    context_object_name = "activity"
    queryset = ResearchActivity.objects.published()
    slug_url_kwarg = "slug"


class NewsListView(ListView):
    template_name = "website/news.html"
    context_object_name = "articles"
    paginate_by = 12

    def get_queryset(self):
        qs = NewsArticle.objects.published()
        category = self.request.GET.get("category")
        if category in {"update", "media"}:
            qs = qs.filter(category=category)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_category"] = self.request.GET.get("category", "")
        return context


class NewsDetailView(DetailView):
    template_name = "website/news_detail.html"
    context_object_name = "article"
    queryset = NewsArticle.objects.published()
    slug_url_kwarg = "slug"


class ContactView(FormView):
    template_name = "website/contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("website:contact")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["site_settings"] = SiteSetting.load()
        return context

    def form_valid(self, form):
        # Honeypot caught nothing and the form is otherwise valid -> save.
        form.save()
        messages.success(
            self.request,
            "Thank you - your message has been received. ZILARD will respond to genuine enquiries as soon as possible.",
        )
        return super().form_valid(form)
