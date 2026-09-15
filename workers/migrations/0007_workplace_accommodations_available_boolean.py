from django.db import migrations, models


def convert_accommodations_to_boolean(apps, schema_editor):
    Workplace = apps.get_model("workers", "Workplace")
    truthy_values = {"1", "true", "yes", "y"}

    for workplace in Workplace.objects.all():
        value = workplace.accommodations_available
        if isinstance(value, bool):
            converted = value
        else:
            text = str(value or "").strip().lower()
            converted = bool(text) and text not in {"0", "false", "no", "n", "none", "not available"}
            if text in truthy_values:
                converted = True
        workplace.accommodations_available = "1" if converted else "0"
        workplace.save(update_fields=["accommodations_available"])


def convert_accommodations_to_text(apps, schema_editor):
    Workplace = apps.get_model("workers", "Workplace")
    for workplace in Workplace.objects.all():
        workplace.accommodations_available = "Yes" if workplace.accommodations_available else ""
        workplace.save(update_fields=["accommodations_available"])


class Migration(migrations.Migration):
    dependencies = [
        ("workers", "0006_seed_trade_union_settings"),
    ]

    operations = [
        migrations.RunPython(convert_accommodations_to_boolean, convert_accommodations_to_text),
        migrations.AlterField(
            model_name="workplace",
            name="accommodations_available",
            field=models.BooleanField(default=False),
        ),
    ]
