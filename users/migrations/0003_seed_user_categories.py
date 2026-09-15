from django.db import migrations


DEFAULT_CATEGORIES = [
    (
        "system_admin",
        "System Admin",
        "Full system access, including settings, users, reports, dashboards, and data management.",
    ),
    (
        "national_manager",
        "National Project Manager",
        "Access to national project data, dashboards, reports, and management workflows.",
    ),
    (
        "union_focal",
        "Trade Union Focal Person",
        "Access focused on assigned union records and union-level coordination.",
    ),
    (
        "data_collector",
        "Data Collector",
        "Data entry and record updating access for field collection workflows.",
    ),
    (
        "read_only",
        "Read-Only",
        "Dashboard, reporting, and viewing access without record editing.",
    ),
]


def seed_user_categories(apps, schema_editor):
    UserCategory = apps.get_model("users", "UserCategory")
    for sort_order, (role, display_name, description) in enumerate(DEFAULT_CATEGORIES, start=1):
        UserCategory.objects.get_or_create(
            role=role,
            defaults={
                "display_name": display_name,
                "description": description,
                "is_active": True,
                "sort_order": sort_order,
            },
        )


def unseed_user_categories(apps, schema_editor):
    UserCategory = apps.get_model("users", "UserCategory")
    UserCategory.objects.filter(role__in=[role for role, _name, _description in DEFAULT_CATEGORIES]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_usercategory"),
    ]

    operations = [
        migrations.RunPython(seed_user_categories, unseed_user_categories),
    ]
