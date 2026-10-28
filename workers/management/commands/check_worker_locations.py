"""Report (and optionally clear) worker and workplace coordinates that do not fit the recorded province.

Before the web "Capture GPS" button used the browser's real location, it filled in a random point, so
some records may have coordinates far from where the worker actually is. This command lists records
whose coordinates are further from their province than is plausible. It changes nothing unless
--clear is given.

Usage:
    python manage.py check_worker_locations            # report only
    python manage.py check_worker_locations --clear    # also clear the flagged coordinates
"""
import math

from django.core.management.base import BaseCommand

from workers.models import Worker, Workplace

# (latitude, longitude, plausible radius in km) -- approximate, deliberately generous.
PROVINCE_AREAS = {
    "Central": (-14.2, 27.9, 300),
    "Copperbelt": (-13.0, 28.3, 200),
    "Eastern": (-13.7, 32.2, 300),
    "Luapula": (-11.1, 29.0, 260),
    "Lusaka": (-15.4, 28.3, 150),
    "Muchinga": (-11.8, 31.6, 320),
    "Northern": (-10.3, 31.0, 320),
    "North-Western": (-12.8, 25.5, 420),
    "Southern": (-16.8, 26.8, 320),
    "Western": (-15.5, 23.5, 380),
}


def distance_km(lat1, lng1, lat2, lng2):
    rad = math.radians
    d_lat, d_lng = rad(lat2 - lat1), rad(lng2 - lng1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(rad(lat1)) * math.cos(rad(lat2)) * math.sin(d_lng / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(a))


class Command(BaseCommand):
    help = "List worker and workplace coordinates that are far from their recorded province."

    def add_arguments(self, parser):
        parser.add_argument("--clear", action="store_true", help="Clear the coordinates of flagged records.")

    def handle(self, *args, **options):
        flagged = []
        for model, label in ((Worker, "Worker"), (Workplace, "Workplace")):
            qs = model.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
            for obj in qs:
                area = PROVINCE_AREAS.get(obj.province)
                if not area:
                    continue
                away = distance_km(float(obj.latitude), float(obj.longitude), area[0], area[1])
                if away > area[2]:
                    name = getattr(obj, "full_name", None) or getattr(obj, "workplace_name", str(obj))
                    flagged.append((label, obj, name, away))

        if not flagged:
            self.stdout.write(self.style.SUCCESS("No coordinates look out of place."))
            return

        self.stdout.write(f"{len(flagged)} record(s) have coordinates far from their province:")
        for label, obj, name, away in flagged:
            self.stdout.write(
                f"  {label} id={obj.pk} {name} | {obj.province}, {obj.district} | "
                f"{obj.latitude}, {obj.longitude} | about {away:.0f} km from the province centre"
            )

        if options["clear"]:
            for _label, obj, _name, _away in flagged:
                obj.latitude = None
                obj.longitude = None
                obj.save(update_fields=["latitude", "longitude"])
            self.stdout.write(self.style.WARNING("Cleared the coordinates above. Re-capture them on the records."))
        else:
            self.stdout.write("Nothing was changed. Re-run with --clear to clear these coordinates.")
