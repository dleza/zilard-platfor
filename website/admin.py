from django.contrib import admin

from .models import (
    ContactMessage,
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


@admin.register(ThematicArea)
class ThematicAreaAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "is_published")
    list_editable = ("order", "is_published")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "summary")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "theme", "status", "start_date", "end_date", "is_published")
    list_filter = ("status", "theme", "is_published")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "summary")


@admin.register(ResearchActivity)
class ResearchActivityAdmin(admin.ModelAdmin):
    list_display = ("title", "year", "status", "theme", "is_published")
    list_filter = ("status", "theme", "year", "is_published")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "purpose", "funder_collaborators")
    ordering = ("-year",)


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ("title", "publication_date", "publication_type", "theme", "is_featured", "is_published")
    list_filter = ("publication_type", "theme", "is_featured", "is_published")
    list_editable = ("is_featured",)
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "authors", "summary")
    date_hierarchy = "publication_date"


@admin.register(HomeSlide)
class HomeSlideAdmin(admin.ModelAdmin):
    list_display = ("display_title", "news_article", "order", "is_published")
    list_editable = ("order", "is_published")
    fields = ("title", "caption", "image", "news_article", "link_url", "order", "is_published")


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "published_date", "source_name", "is_published")
    list_filter = ("category", "theme", "is_published")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "summary", "source_name")
    date_hierarchy = "published_date"


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ("full_name", "position", "group", "order", "is_published")
    list_editable = ("order", "is_published")
    list_filter = ("group",)


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ("name", "relationship", "period", "order", "is_published")
    list_editable = ("order", "is_published")


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SiteSetting.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "category", "organisation", "submitted_at", "is_handled")
    list_filter = ("category", "is_handled")
    list_editable = ("is_handled",)
    search_fields = ("name", "email", "organisation", "message")
    readonly_fields = ("name", "email", "organisation", "category", "message", "submitted_at")
