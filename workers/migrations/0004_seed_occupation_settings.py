from django.db import migrations


DEFAULT_OCCUPATIONS = [
    "Machine operator",
    "Teacher",
    "Clerk",
    "Security officer",
    "Nurse aide",
    "Driver",
    "Market trader",
    "Mine technician",
    "Tailor",
    "Warehouse assistant",
    "Community organiser",
    "Receptionist",
]


def seed_occupations(apps, schema_editor):
    Occupation = apps.get_model("workers", "Occupation")
    Worker = apps.get_model("workers", "Worker")

    names = list(DEFAULT_OCCUPATIONS)
    existing_worker_occupations = (
        Worker.objects.exclude(occupation="")
        .values_list("occupation", flat=True)
        .distinct()
    )
    for name in existing_worker_occupations:
        if name not in names:
            names.append(name)

    for sort_order, name in enumerate(names, start=1):
        Occupation.objects.get_or_create(
            name=name,
            defaults={"is_active": True, "sort_order": sort_order},
        )


def unseed_occupations(apps, schema_editor):
    Occupation = apps.get_model("workers", "Occupation")
    Occupation.objects.filter(name__in=DEFAULT_OCCUPATIONS).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("workers", "0003_occupation"),
    ]

    operations = [
        migrations.RunPython(seed_occupations, unseed_occupations),
    ]
