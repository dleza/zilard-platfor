import random
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from monitoring.models import ProjectActivity, TrainingAttendance
from users.models import UserCategory
from workers.choices import (
    COMMON_UNIONS,
    DISABILITY_TYPE_CHOICES,
    EMPLOYMENT_STATUS_CHOICES,
    GENDER_CHOICES,
    PROVINCE_DISTRICTS,
    PROVINCE_CHOICES,
    SECTOR_CHOICES,
    SEVERITY_CHOICES,
)
from workers.models import AccessibilityAudit, DisabilityProfile, LabourRightsRecord, Occupation, TradeUnion, Worker, Workplace


PROVINCE_COORDS = {
    "Central": (-14.45, 28.45),
    "Copperbelt": (-12.95, 28.65),
    "Eastern": (-13.65, 32.65),
    "Luapula": (-11.25, 29.05),
    "Lusaka": (-15.42, 28.28),
    "Muchinga": (-11.85, 31.45),
    "Northern": (-10.22, 31.18),
    "North-Western": (-12.18, 26.40),
    "Southern": (-16.82, 26.98),
    "Western": (-15.25, 23.13),
}

FIRST_NAMES = [
    "Misozi",
    "Chanda",
    "Mutinta",
    "Mwansa",
    "Bupe",
    "Mwaka",
    "Kelvin",
    "Thandiwe",
    "Lombe",
    "Joseph",
    "Natasha",
    "Patrick",
    "Ireen",
    "Bwalya",
    "Tisa",
    "Moses",
]

LAST_NAMES = [
    "Phiri",
    "Banda",
    "Tembo",
    "Mulenga",
    "Sakala",
    "Mumba",
    "Chileshe",
    "Mwanza",
    "Daka",
    "Zulu",
    "Nyirenda",
    "Sichone",
]

EMPLOYERS = [
    "Kafue Textiles Cooperative",
    "Copperbelt Mine Services",
    "Chipata Agro Processing",
    "Lusaka Municipal Services",
    "Mongu Fish Traders Association",
    "Ndola Teaching Hospital",
    "Choma Milling Company",
    "Solwezi Logistics Hub",
    "Kasama Teachers Resource Centre",
    "Mansa Water Utility",
    "Livingstone Hospitality Group",
    "Kitwe Manufacturing Yard",
]

OCCUPATIONS = [
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


class Command(BaseCommand):
    help = "Load demo users and realistic sample data for the prototype."

    def add_arguments(self, parser):
        parser.add_argument("--workers", type=int, default=75, help="Number of worker records to create.")

    def handle(self, *args, **options):
        random.seed(2026)
        worker_count = max(options["workers"], 50)
        self.create_user_categories()
        admin = self.create_users()
        self.create_occupations()
        self.create_trade_unions()
        workplaces = self.create_workplaces()
        workers = self.create_workers(worker_count, workplaces, admin)
        self.create_project_activities(workers)
        self.stdout.write(self.style.SUCCESS(f"Loaded demo users, {len(workplaces)} workplaces, and {len(workers)} workers."))
        self.stdout.write("Demo password for all seeded users: ChangeMe!2026")

    def create_user_categories(self):
        User = get_user_model()
        categories = [
            (
                User.ROLE_SYSTEM_ADMIN,
                "System Admin",
                "Full system access, including settings, users, reports, dashboards, and data management.",
            ),
            (
                User.ROLE_NATIONAL_MANAGER,
                "National Project Manager",
                "Access to national project data, dashboards, reports, and management workflows.",
            ),
            (
                User.ROLE_UNION_FOCAL,
                "Trade Union Focal Person",
                "Access focused on assigned union records and union-level coordination.",
            ),
            (
                User.ROLE_DATA_COLLECTOR,
                "Data Collector",
                "Data entry and record updating access for field collection workflows.",
            ),
            (
                User.ROLE_READ_ONLY,
                "Read-Only",
                "Dashboard, reporting, and viewing access without record editing.",
            ),
        ]
        for sort_order, (role, display_name, description) in enumerate(categories, start=1):
            UserCategory.objects.update_or_create(
                role=role,
                defaults={
                    "display_name": display_name,
                    "description": description,
                    "is_active": True,
                    "sort_order": sort_order,
                },
            )

    def create_users(self):
        User = get_user_model()
        users = [
            ("admin", "admin@example.org", "System", "Admin", User.ROLE_SYSTEM_ADMIN, "", True, True),
            ("manager", "manager@example.org", "National", "Manager", User.ROLE_NATIONAL_MANAGER, "", True, False),
            ("focal_muz", "focal.muz@example.org", "MUZ", "Focal", User.ROLE_UNION_FOCAL, "MUZ", False, False),
            ("collector_muz", "collector.muz@example.org", "MUZ", "Collector", User.ROLE_DATA_COLLECTOR, "MUZ", False, False),
            ("readonly", "readonly@example.org", "Read", "Only", User.ROLE_READ_ONLY, "", False, False),
        ]
        first_user = None
        for username, email, first_name, last_name, role, assigned_union, is_staff, is_superuser in users:
            user, _created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                    "role": role,
                    "organisation": "ZILARD/ZCTU Prototype",
                    "assigned_union": assigned_union,
                    "is_staff": is_staff,
                    "is_superuser": is_superuser,
                },
            )
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.role = role
            user.organisation = "ZILARD/ZCTU Prototype"
            user.assigned_union = assigned_union
            user.is_staff = is_staff
            user.is_superuser = is_superuser
            user.set_password("ChangeMe!2026")
            user.save()
            if first_user is None:
                first_user = user
        return first_user

    def create_occupations(self):
        for sort_order, name in enumerate(OCCUPATIONS, start=1):
            Occupation.objects.update_or_create(
                name=name,
                defaults={
                    "is_active": True,
                    "sort_order": sort_order,
                },
            )

    def create_trade_unions(self):
        for sort_order, name in enumerate(COMMON_UNIONS, start=1):
            TradeUnion.objects.update_or_create(
                name=name,
                defaults={
                    "is_active": True,
                    "sort_order": sort_order,
                },
            )

    def create_workplaces(self):
        workplaces = []
        sectors = [choice[0] for choice in SECTOR_CHOICES]
        accessibility = ["accessible", "partially_accessible", "not_accessible", "not_assessed"]
        for idx, employer in enumerate(EMPLOYERS, start=1):
            province = random.choice([choice[0] for choice in PROVINCE_CHOICES])
            lat, lng = self.jitter(PROVINCE_COORDS[province])
            workplace, _created = Workplace.objects.update_or_create(
                employer_name=employer,
                defaults={
                    "workplace_name": f"{employer.split()[0]} Site {idx}",
                    "province": province,
                    "district": random.choice(PROVINCE_DISTRICTS[province]),
                    "address": f"Plot {100 + idx}, Industrial Area",
                    "sector": random.choice(sectors),
                    "latitude": lat,
                    "longitude": lng,
                    "accessibility_status": random.choice(accessibility),
                    "accommodations_available": random.choice([True, False]),
                    "union_presence": random.choice([True, False]),
                },
            )
            workplaces.append(workplace)
            AccessibilityAudit.objects.get_or_create(
                workplace=workplace,
                audit_date=timezone.localdate() - timedelta(days=random.randint(5, 180)),
                auditor_name=random.choice(["ZAFOD audit team", "ZCTU focal person", "ZILARD researcher"]),
                defaults={
                    "entrance_score": random.randint(1, 5),
                    "restroom_score": random.randint(1, 5),
                    "workstation_score": random.randint(1, 5),
                    "transport_score": random.randint(1, 5),
                    "findings": "Prototype sample audit covering entrance, restroom, workstation and transport access.",
                    "recommendations": "Prioritise low-cost reasonable accommodations and workplace committee follow-up.",
                },
            )
        return workplaces

    def create_workers(self, count, workplaces, admin):
        workers = []
        genders = [choice[0] for choice in GENDER_CHOICES]
        disabilities = [choice[0] for choice in DISABILITY_TYPE_CHOICES]
        severities = [choice[0] for choice in SEVERITY_CHOICES]
        employment_statuses = [choice[0] for choice in EMPLOYMENT_STATUS_CHOICES]
        sectors = [choice[0] for choice in SECTOR_CHOICES]
        current_year = timezone.localdate().year

        for idx in range(1, count + 1):
            province = random.choice([choice[0] for choice in PROVINCE_CHOICES])
            lat, lng = self.jitter(PROVINCE_COORDS[province])
            workplace = random.choice(workplaces)
            age = random.randint(19, 62)
            dob = date(current_year - age, random.randint(1, 12), random.randint(1, 28))
            union_name = random.choice(COMMON_UNIONS + ["", ""])
            capture_source = random.choice(
                [Worker.CAPTURE_SOURCE_WEB, Worker.CAPTURE_SOURCE_MOBILE, Worker.CAPTURE_SOURCE_MOBILE]
            )
            capture_mode = (
                Worker.CAPTURE_MODE_OFFLINE
                if capture_source == Worker.CAPTURE_SOURCE_MOBILE and random.random() < 0.35
                else Worker.CAPTURE_MODE_ONLINE
            )
            worker, _created = Worker.objects.update_or_create(
                unique_id=f"DLDMS-SAMPLE-{idx:03d}",
                defaults={
                    "first_name": random.choice(FIRST_NAMES),
                    "last_name": random.choice(LAST_NAMES),
                    "nationality": "Zambian",
                    "gender": random.choice(genders),
                    "date_of_birth": dob,
                    "phone": f"+26097{random.randint(1000000, 9999999)}",
                    "email": "",
                    "province": province,
                    "district": random.choice(PROVINCE_DISTRICTS[province]),
                    "workplace": workplace,
                    "sector": workplace.sector if random.random() < 0.75 else random.choice(sectors),
                    "occupation": random.choice(OCCUPATIONS),
                    "employment_status": random.choice(employment_statuses),
                    "union_membership_status": "member" if union_name else random.choice(["not_member", "unknown"]),
                    "union_name": union_name,
                    "leadership_participation": random.random() < 0.18,
                    "committee_participation": random.random() < 0.24,
                    "organising_activities": random.choice(
                        [
                            "",
                            "Participated in workplace inclusion committee.",
                            "Joined union organising outreach.",
                            "Requested disability inclusion training for shop stewards.",
                        ]
                    ),
                    "latitude": lat,
                    "longitude": lng,
                    "consent_to_store_data": True,
                    "data_verified": random.random() < 0.68,
                    "verified_at": timezone.now() if random.random() < 0.68 else None,
                    "capture_source": capture_source,
                    "capture_mode": capture_mode,
                    "captured_at_device": timezone.now() if capture_mode == Worker.CAPTURE_MODE_OFFLINE else None,
                    "created_by": admin,
                    "updated_by": admin,
                },
            )
            DisabilityProfile.objects.update_or_create(
                worker=worker,
                defaults={
                    "disability_type": random.choice(disabilities),
                    "severity": random.choice(severities),
                    "assistive_devices": random.choice(
                        ["Wheelchair", "White cane", "Hearing aid", "Crutches", "None recorded", "Screen reader"]
                    ),
                    "accommodation_requirements": random.choice(
                        [
                            "Flexible reporting time",
                            "Accessible workstation",
                            "Sign language interpretation",
                            "Accessible transport support",
                            "Written instructions in accessible format",
                        ]
                    ),
                    "accessibility_challenges": random.choice(
                        [
                            "Uneven entrance surface",
                            "Inaccessible restroom",
                            "Limited assistive technology",
                            "Communication barriers during staff meetings",
                            "No major challenge recorded",
                        ]
                    ),
                    "functional_limitations": "Washington Group short-set inspired responses captured for prototype.",
                    "wg_seeing": random.randint(0, 3),
                    "wg_hearing": random.randint(0, 3),
                    "wg_walking": random.randint(0, 3),
                    "wg_remembering": random.randint(0, 3),
                    "wg_self_care": random.randint(0, 3),
                    "wg_communicating": random.randint(0, 3),
                },
            )
            LabourRightsRecord.objects.update_or_create(
                worker=worker,
                defaults={
                    "grievance_reported": random.random() < 0.22,
                    "grievance_summary": random.choice(
                        [
                            "",
                            "Requested support on workplace accommodation delay.",
                            "Reported exclusion from training opportunity.",
                            "Asked for guidance on collective bargaining coverage.",
                        ]
                    ),
                    "case_status": random.choice(["none", "open", "monitoring", "referred", "resolved"]),
                    "legal_support_provided": random.random() < 0.18,
                    "collective_bargaining_coverage": random.random() < 0.55,
                    "social_protection_coverage": random.random() < 0.58,
                },
            )
            workers.append(worker)
        return workers

    def create_project_activities(self, workers):
        for idx, activity_type in enumerate(["training", "workshop", "audit", "employer_engagement", "advocacy"], start=1):
            province = random.choice([choice[0] for choice in PROVINCE_CHOICES])
            activity, _created = ProjectActivity.objects.update_or_create(
                title=f"Prototype {activity_type.replace('_', ' ').title()} {idx}",
                defaults={
                    "activity_type": activity_type,
                    "partner": random.choice(["ZCTU", "ZAFOD", "ZILARD", "SASK"]),
                    "province": province,
                    "district": random.choice(PROVINCE_DISTRICTS[province]),
                    "start_date": timezone.localdate() - timedelta(days=idx * 21),
                    "participants_total": random.randint(18, 55),
                    "participants_with_disabilities": random.randint(8, 30),
                    "notes": "Seeded activity for dashboard and monitoring demonstrations.",
                },
            )
            for worker in random.sample(workers, min(12, len(workers))):
                TrainingAttendance.objects.get_or_create(
                    activity=activity,
                    worker=worker,
                    defaults={
                        "role": "participant",
                        "attended": random.random() < 0.9,
                        "certificate_issued": random.random() < 0.55,
                    },
                )

    @staticmethod
    def jitter(coords):
        lat, lng = coords
        return round(lat + random.uniform(-0.45, 0.45), 6), round(lng + random.uniform(-0.45, 0.45), 6)
