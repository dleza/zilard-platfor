from django.db import migrations


def backfill_history(apps, schema_editor):
    """Give every existing worker one starting history entry, so the history is never empty."""
    Worker = apps.get_model("workers", "Worker")
    History = apps.get_model("workers", "EmploymentStatusHistory")
    existing = set(History.objects.values_list("worker_id", flat=True))
    entries = [
        History(
            worker_id=worker.pk,
            status=worker.employment_status,
            effective_date=worker.created_at.date(),
            note="Initial status (existing record)",
        )
        for worker in Worker.objects.all().only("id", "employment_status", "created_at")
        if worker.pk not in existing
    ]
    History.objects.bulk_create(entries, batch_size=500)


class Migration(migrations.Migration):
    dependencies = [
        ("workers", "0009_disability_description_employment_history"),
    ]

    operations = [
        migrations.RunPython(backfill_history, migrations.RunPython.noop),
    ]
