import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ThematicArea",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=160)),
                ("slug", models.SlugField(max_length=180, unique=True)),
                ("summary", models.CharField(help_text="One or two sentences shown on the homepage panel and work list.", max_length=280)),
                ("body", models.TextField(blank=True, help_text="What issue this addresses, what ZILARD has done, what visitors can read.")),
                ("order", models.PositiveIntegerField(default=0)),
                ("is_published", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "Thematic area",
                "verbose_name_plural": "Thematic areas (Our Work)",
                "ordering": ["order", "title"],
            },
        ),
        migrations.CreateModel(
            name="TeamMember",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("full_name", models.CharField(max_length=150)),
                ("position", models.CharField(max_length=200)),
                ("group", models.CharField(choices=[("board", "Board of Directors"), ("management", "Management"), ("staff", "Staff"), ("researcher", "Associated researcher")], default="management", max_length=20)),
                ("bio", models.TextField(blank=True)),
                ("photo", models.ImageField(blank=True, null=True, upload_to="team/")),
                ("order", models.PositiveIntegerField(default=0)),
                ("is_published", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ["group", "order", "full_name"],
            },
        ),
        migrations.CreateModel(
            name="SiteSetting",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("office_address", models.CharField(blank=True, max_length=300)),
                ("phone", models.CharField(blank=True, max_length=60)),
                ("mobile", models.CharField(blank=True, max_length=60)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("office_hours", models.CharField(blank=True, max_length=150)),
                ("facebook_url", models.URLField(blank=True)),
                ("linkedin_url", models.URLField(blank=True)),
                ("twitter_url", models.URLField(blank=True)),
            ],
            options={
                "verbose_name": "Site settings",
                "verbose_name_plural": "Site settings",
            },
        ),
        migrations.CreateModel(
            name="ContactMessage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150)),
                ("email", models.EmailField(max_length=254)),
                ("organisation", models.CharField(blank=True, max_length=200)),
                ("category", models.CharField(choices=[("research", "Research and Publications"), ("collaboration", "Collaboration"), ("media", "Media"), ("general", "General Enquiries")], default="general", max_length=20)),
                ("message", models.TextField()),
                ("submitted_at", models.DateTimeField(auto_now_add=True)),
                ("is_handled", models.BooleanField(default=False)),
            ],
            options={
                "ordering": ["-submitted_at"],
            },
        ),
        migrations.CreateModel(
            name="Project",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("slug", models.SlugField(max_length=220, unique=True)),
                ("status", models.CharField(choices=[("planned", "Planned"), ("ongoing", "Ongoing"), ("completed", "Completed")], default="ongoing", max_length=20)),
                ("start_date", models.DateField(blank=True, null=True)),
                ("end_date", models.DateField(blank=True, null=True)),
                ("summary", models.CharField(max_length=280)),
                ("role", models.CharField(blank=True, help_text="ZILARD's specific role, e.g. lead researcher, implementing partner.", max_length=255)),
                ("participating_organisations", models.CharField(blank=True, max_length=400)),
                ("body", models.TextField(blank=True, help_text="Objectives, activities, approved details.")),
                ("is_published", models.BooleanField(default=True)),
                ("theme", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="projects", to="website.thematicarea")),
            ],
            options={
                "ordering": ["-start_date", "title"],
            },
        ),
        migrations.CreateModel(
            name="ResearchActivity",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=250)),
                ("slug", models.SlugField(max_length=270, unique=True)),
                ("year", models.PositiveIntegerField()),
                ("status", models.CharField(choices=[("completed", "Completed"), ("ongoing", "Ongoing"), ("planned", "Planned")], default="completed", max_length=20)),
                ("purpose", models.TextField(help_text="Why the study was undertaken.")),
                ("geographic_coverage", models.CharField(blank=True, max_length=200)),
                ("funder_collaborators", models.CharField(blank=True, max_length=300)),
                ("available_outputs", models.CharField(blank=True, help_text="e.g. 'Full report', 'Summary only', 'Manual (pending release)'.", max_length=300)),
                ("is_published", models.BooleanField(default=True)),
                ("theme", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="research_activities", to="website.thematicarea")),
            ],
            options={
                "verbose_name_plural": "Research activities (portfolio)",
                "ordering": ["-year", "title"],
            },
        ),
        migrations.CreateModel(
            name="Publication",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=250)),
                ("slug", models.SlugField(max_length=270, unique=True)),
                ("authors", models.CharField(blank=True, max_length=300)),
                ("publication_date", models.DateField()),
                ("publication_type", models.CharField(choices=[("report", "Research report"), ("brief", "Policy brief"), ("summary", "Research summary"), ("manual", "Training manual / tool")], default="report", max_length=20)),
                ("summary", models.TextField(help_text="Plain-language summary, ~100-150 words.")),
                ("key_findings", models.TextField(blank=True, help_text="One finding per line.")),
                ("cover_image", models.ImageField(blank=True, null=True, upload_to="publications/covers/")),
                ("document", models.FileField(blank=True, null=True, upload_to="publications/files/")),
                ("external_url", models.URLField(blank=True, help_text="Link to the report on its original hosting site (SASK, FES, etc.), if applicable.")),
                ("acknowledgements", models.TextField(blank=True, help_text="Funders/partners and suggested citation.")),
                ("is_featured", models.BooleanField(default=False)),
                ("is_published", models.BooleanField(default=True)),
                ("research_activity", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="publications", to="website.researchactivity")),
                ("theme", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="publications", to="website.thematicarea")),
            ],
            options={
                "ordering": ["-publication_date"],
            },
        ),
        migrations.CreateModel(
            name="NewsArticle",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=250)),
                ("slug", models.SlugField(max_length=270, unique=True)),
                ("category", models.CharField(choices=[("update", "ZILARD update"), ("media", "ZILARD in the media")], default="update", max_length=10)),
                ("published_date", models.DateField(default=django.utils.timezone.now)),
                ("location", models.CharField(blank=True, max_length=150)),
                ("source_name", models.CharField(blank=True, help_text="Original publisher, for 'ZILARD in the media' items.", max_length=150)),
                ("source_url", models.URLField(blank=True)),
                ("summary", models.CharField(max_length=300)),
                ("body", models.TextField(blank=True)),
                ("cover_image", models.ImageField(blank=True, null=True, upload_to="news/covers/")),
                ("is_published", models.BooleanField(default=True)),
                ("theme", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="news_articles", to="website.thematicarea")),
            ],
            options={
                "verbose_name_plural": "News & events",
                "ordering": ["-published_date"],
            },
        ),
        migrations.CreateModel(
            name="Partner",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("relationship", models.CharField(help_text="Nature of the collaboration, e.g. 'Commissioned and supported the 2023 disability study'.", max_length=300)),
                ("period", models.CharField(blank=True, max_length=100)),
                ("logo", models.ImageField(blank=True, null=True, upload_to="partners/")),
                ("order", models.PositiveIntegerField(default=0)),
                ("is_published", models.BooleanField(default=True)),
                ("related_publication", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="partners", to="website.publication")),
            ],
            options={
                "ordering": ["order", "name"],
            },
        ),
    ]
