from django.db import migrations


DEFAULT_UNIONS = [
    "ZCTU",
    "MUZ",
    "BETUZ",
    "NUPSW",
    "ZUFIAW",
    "ZULAWU",
    "NAQEZ",
    "SESTUZ",
    "ZRAWU",
]


def seed_trade_unions(apps, schema_editor):
    TradeUnion = apps.get_model("workers", "TradeUnion")
    Worker = apps.get_model("workers", "Worker")
    User = apps.get_model("users", "User")

    names = list(DEFAULT_UNIONS)
    existing_worker_unions = Worker.objects.exclude(union_name="").values_list("union_name", flat=True).distinct()
    existing_user_unions = User.objects.exclude(assigned_union="").values_list("assigned_union", flat=True).distinct()

    for name in list(existing_worker_unions) + list(existing_user_unions):
        if name and name not in names:
            names.append(name)

    for sort_order, name in enumerate(names, start=1):
        TradeUnion.objects.get_or_create(
            name=name,
            defaults={"is_active": True, "sort_order": sort_order},
        )


def unseed_trade_unions(apps, schema_editor):
    TradeUnion = apps.get_model("workers", "TradeUnion")
    TradeUnion.objects.filter(name__in=DEFAULT_UNIONS).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
        ("workers", "0005_tradeunion"),
    ]

    operations = [
        migrations.RunPython(seed_trade_unions, unseed_trade_unions),
    ]
