from django.test import TestCase
from django.urls import reverse

from users.models import User
from workers.models import Worker


class ReportExportTests(TestCase):
    def setUp(self):
        Worker.objects.create(
            first_name="Chanda",
            last_name="Mwansa",
            gender="female",
            province="Central",
            district="Chibombo",
            sector="agriculture",
            employment_status="formal",
        )
        self.admin = User.objects.create_user(username="admin_r", password="pw", role=User.ROLE_SYSTEM_ADMIN)
        self.client.login(username="admin_r", password="pw")

    def test_report_index_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("reports:index"))
        self.assertNotEqual(response.status_code, 200)

    def test_report_index_loads(self):
        response = self.client.get(reverse("reports:index"))
        self.assertEqual(response.status_code, 200)

    def test_csv_export_returns_csv(self):
        response = self.client.get(reverse("reports:workers-csv"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/csv", response["Content-Type"])
        self.assertIn(b"Chanda", response.content)

    def test_xlsx_export_returns_spreadsheet(self):
        response = self.client.get(reverse("reports:workers-xlsx"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("spreadsheetml", response["Content-Type"])

    def test_pdf_summary_returns_pdf(self):
        response = self.client.get(reverse("reports:summary-pdf"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
