from django.urls import path

from .views import ReportIndexView, export_workers_csv, export_workers_xlsx, summary_pdf

app_name = "reports"

urlpatterns = [
    path("", ReportIndexView.as_view(), name="index"),
    path("export/workers.csv", export_workers_csv, name="workers-csv"),
    path("export/workers.xlsx", export_workers_xlsx, name="workers-xlsx"),
    path("pdf/summary/", summary_pdf, name="summary-pdf"),
]
