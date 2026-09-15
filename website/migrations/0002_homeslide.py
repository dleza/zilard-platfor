import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="HomeSlide",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(blank=True, help_text="Leave blank to use the linked news article's title.", max_length=200)),
                ("caption", models.CharField(blank=True, help_text="Leave blank to use the linked news article's summary.", max_length=280)),
                ("image", models.ImageField(blank=True, help_text="Optional. If left empty and a news article is linked, the article's cover image (if any) is used.", null=True, upload_to="slides/")),
                ("link_url", models.URLField(blank=True, help_text="Optional external link, used if no news article is linked.")),
                ("order", models.PositiveIntegerField(default=0)),
                ("is_published", models.BooleanField(default=True)),
                ("news_article", models.ForeignKey(blank=True, help_text="Optional. Pulls title/summary/link from a News & Events item.", null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="slides", to="website.newsarticle")),
            ],
            options={
                "ordering": ["order", "id"],
            },
        ),
    ]
