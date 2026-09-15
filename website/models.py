"""Public website content models.

These are deliberately separate from the internal DLDMS data-collection
models (workers, workplaces, monitoring): this app is the institutional,
publicly-readable side of the project -- what ZILARD is, what it works on,
and what it has published -- managed through the Django admin by whoever
ZILARD designates as the content owner/approver.
"""
from django.db import models
from django.urls import reverse
from django.utils import timezone


class PublishedQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True)


class ThematicArea(models.Model):
    """One of ZILARD's core areas of expertise (Our Work)."""

    title = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True)
    summary = models.CharField(
        max_length=280,
        help_text="One or two sentences shown on the homepage panel and work list.",
    )
    body = models.TextField(
        help_text="What issue this addresses, what ZILARD has done, what visitors can read.",
        blank=True,
    )
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    objects = PublishedQuerySet.as_manager()

    class Meta:
        ordering = ["order", "title"]
        verbose_name = "Thematic area"
        verbose_name_plural = "Thematic areas (Our Work)"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("website:work-detail", args=[self.slug])


class Project(models.Model):
    """A time-bound programme or project, distinct from an ongoing theme."""

    STATUS_CHOICES = [
        ("planned", "Planned"),
        ("ongoing", "Ongoing"),
        ("completed", "Completed"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    theme = models.ForeignKey(
        ThematicArea, on_delete=models.SET_NULL, null=True, blank=True, related_name="projects"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ongoing")
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    summary = models.CharField(max_length=280)
    role = models.CharField(
        max_length=255, blank=True, help_text="ZILARD's specific role, e.g. lead researcher, implementing partner."
    )
    participating_organisations = models.CharField(max_length=400, blank=True)
    body = models.TextField(blank=True, help_text="Objectives, activities, approved details.")
    is_published = models.BooleanField(default=True)

    objects = PublishedQuerySet.as_manager()

    class Meta:
        ordering = ["-start_date", "title"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("website:project-detail", args=[self.slug])


class ResearchActivity(models.Model):
    """An entry in the research portfolio -- a study or output, which may or
    may not have an associated downloadable Publication yet."""

    STATUS_CHOICES = [
        ("completed", "Completed"),
        ("ongoing", "Ongoing"),
        ("planned", "Planned"),
    ]

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=270, unique=True)
    year = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="completed")
    purpose = models.TextField(help_text="Why the study was undertaken.")
    geographic_coverage = models.CharField(max_length=200, blank=True)
    funder_collaborators = models.CharField(max_length=300, blank=True)
    theme = models.ForeignKey(
        ThematicArea, on_delete=models.SET_NULL, null=True, blank=True, related_name="research_activities"
    )
    available_outputs = models.CharField(
        max_length=300, blank=True, help_text="e.g. 'Full report', 'Summary only', 'Manual (pending release)'."
    )
    is_published = models.BooleanField(default=True)

    objects = PublishedQuerySet.as_manager()

    class Meta:
        ordering = ["-year", "title"]
        verbose_name_plural = "Research activities (portfolio)"

    def __str__(self):
        return f"{self.title} ({self.year})"

    def get_absolute_url(self):
        return reverse("website:research-activity-detail", args=[self.slug])


class Publication(models.Model):
    """A publicly readable/downloadable research output."""

    TYPE_CHOICES = [
        ("report", "Research report"),
        ("brief", "Policy brief"),
        ("summary", "Research summary"),
        ("manual", "Training manual / tool"),
    ]

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=270, unique=True)
    authors = models.CharField(max_length=300, blank=True)
    publication_date = models.DateField()
    publication_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="report")
    theme = models.ForeignKey(
        ThematicArea, on_delete=models.SET_NULL, null=True, blank=True, related_name="publications"
    )
    research_activity = models.ForeignKey(
        ResearchActivity, on_delete=models.SET_NULL, null=True, blank=True, related_name="publications"
    )
    summary = models.TextField(help_text="Plain-language summary, ~100-150 words.")
    key_findings = models.TextField(blank=True, help_text="One finding per line.")
    cover_image = models.ImageField(upload_to="publications/covers/", blank=True, null=True)
    document = models.FileField(upload_to="publications/files/", blank=True, null=True)
    external_url = models.URLField(
        blank=True, help_text="Link to the report on its original hosting site (SASK, FES, etc.), if applicable."
    )
    acknowledgements = models.TextField(blank=True, help_text="Funders/partners and suggested citation.")
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)

    objects = PublishedQuerySet.as_manager()

    class Meta:
        ordering = ["-publication_date"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("website:publication-detail", args=[self.slug])

    @property
    def key_findings_list(self):
        return [line.strip() for line in self.key_findings.splitlines() if line.strip()]


class NewsArticle(models.Model):
    """Either a ZILARD-authored update, or an external media mention."""

    CATEGORY_CHOICES = [
        ("update", "ZILARD update"),
        ("media", "ZILARD in the media"),
    ]

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=270, unique=True)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default="update")
    published_date = models.DateField(default=timezone.now)
    location = models.CharField(max_length=150, blank=True)
    source_name = models.CharField(
        max_length=150, blank=True, help_text="Original publisher, for 'ZILARD in the media' items."
    )
    source_url = models.URLField(blank=True)
    summary = models.CharField(max_length=300)
    body = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to="news/covers/", blank=True, null=True)
    theme = models.ForeignKey(
        ThematicArea, on_delete=models.SET_NULL, null=True, blank=True, related_name="news_articles"
    )
    is_published = models.BooleanField(default=True)

    objects = PublishedQuerySet.as_manager()

    class Meta:
        ordering = ["-published_date"]
        verbose_name_plural = "News & events"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("website:news-detail", args=[self.slug])


class TeamMember(models.Model):
    GROUP_CHOICES = [
        ("board", "Board of Directors"),
        ("management", "Management"),
        ("staff", "Staff"),
        ("researcher", "Associated researcher"),
    ]

    full_name = models.CharField(max_length=150)
    position = models.CharField(max_length=200)
    group = models.CharField(max_length=20, choices=GROUP_CHOICES, default="management")
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to="team/", blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    objects = PublishedQuerySet.as_manager()

    class Meta:
        ordering = ["group", "order", "full_name"]

    def __str__(self):
        return f"{self.full_name} ({self.get_group_display()})"


class Partner(models.Model):
    """A documented collaboration -- kept relationship-specific rather than
    an unqualified 'current partner' claim."""

    name = models.CharField(max_length=200)
    relationship = models.CharField(
        max_length=300, help_text="Nature of the collaboration, e.g. 'Commissioned and supported the 2023 disability study'."
    )
    related_publication = models.ForeignKey(
        Publication, on_delete=models.SET_NULL, null=True, blank=True, related_name="partners"
    )
    period = models.CharField(max_length=100, blank=True)
    logo = models.ImageField(upload_to="partners/", blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    objects = PublishedQuerySet.as_manager()

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class SiteSetting(models.Model):
    """Singleton-ish key institutional details editable without a deploy.

    Kept deliberately small: confirmed contact details and social links only.
    """

    office_address = models.CharField(max_length=300, blank=True)
    phone = models.CharField(max_length=60, blank=True)
    mobile = models.CharField(max_length=60, blank=True)
    email = models.EmailField(blank=True)
    office_hours = models.CharField(max_length=150, blank=True)
    facebook_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self):
        return "Site settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class HomeSlide(models.Model):
    """One slide in the homepage carousel.

    A slide can be a straightforward uploaded photo, or it can point at an
    existing News & Events item (title/summary/link come from the article
    if no image is uploaded) -- so the same carousel can mix approved
    photography with rotating news bulletins without duplicating content.
    """

    title = models.CharField(max_length=200, blank=True, help_text="Leave blank to use the linked news article's title.")
    caption = models.CharField(max_length=280, blank=True, help_text="Leave blank to use the linked news article's summary.")
    image = models.ImageField(
        upload_to="slides/", blank=True, null=True,
        help_text="Optional. If left empty and a news article is linked, the article's cover image (if any) is used.",
    )
    news_article = models.ForeignKey(
        NewsArticle, on_delete=models.SET_NULL, null=True, blank=True, related_name="slides",
        help_text="Optional. Pulls title/summary/link from a News & Events item.",
    )
    link_url = models.URLField(blank=True, help_text="Optional external link, used if no news article is linked.")
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    objects = PublishedQuerySet.as_manager()

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.display_title

    @property
    def display_title(self):
        return self.title or (self.news_article.title if self.news_article_id else "Untitled slide")

    @property
    def display_caption(self):
        return self.caption or (self.news_article.summary if self.news_article_id else "")

    @property
    def display_image(self):
        if self.image:
            return self.image
        if self.news_article_id and self.news_article.cover_image:
            return self.news_article.cover_image
        return None

    @property
    def display_url(self):
        if self.news_article_id:
            return self.news_article.get_absolute_url()
        return self.link_url

    @property
    def display_tag(self):
        if self.news_article_id:
            return self.news_article.get_category_display()
        return ""


class EnquiryCategory(models.TextChoices):
    RESEARCH = "research", "Research and Publications"
    COLLABORATION = "collaboration", "Collaboration"
    MEDIA = "media", "Media"
    GENERAL = "general", "General Enquiries"


class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    organisation = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=20, choices=EnquiryCategory.choices, default=EnquiryCategory.GENERAL)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_handled = models.BooleanField(default=False)

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.name} - {self.get_category_display()} ({self.submitted_at:%Y-%m-%d})"
