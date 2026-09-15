from django import forms

from workers.choices import (
    DISABILITY_TYPE_CHOICES,
    EMPLOYMENT_STATUS_CHOICES,
    GENDER_CHOICES,
    GROUPED_DISTRICT_CHOICES,
    PROVINCE_CHOICES,
    SECTOR_CHOICES,
)
from workers.models import TradeUnion, Worker


REPORT_CHOICES = [
    ("workers", "Worker register"),
    ("disability", "Disability summary"),
    ("workplaces", "Workplace accessibility"),
    ("labour", "Labour rights"),
    ("activities", "Project activities"),
    ("feedback", "Stakeholder feedback"),
]


class ReportFilterForm(forms.Form):
    report = forms.ChoiceField(choices=REPORT_CHOICES, required=True)
    q = forms.CharField(label="Search", required=False)
    province = forms.ChoiceField(
        choices=[("", "All provinces")] + PROVINCE_CHOICES,
        required=False,
        widget=forms.Select(attrs={"data-province-select": "true"}),
    )
    district = forms.ChoiceField(
        choices=[("", "All districts")] + GROUPED_DISTRICT_CHOICES,
        required=False,
        widget=forms.Select(attrs={"data-district-select": "true"}),
    )
    gender = forms.ChoiceField(choices=[("", "All genders")] + GENDER_CHOICES, required=False)
    disability_type = forms.ChoiceField(
        choices=[("", "All disability types")] + DISABILITY_TYPE_CHOICES,
        required=False,
    )
    sector = forms.ChoiceField(choices=[("", "All sectors")] + SECTOR_CHOICES, required=False)
    employment_status = forms.ChoiceField(
        choices=[("", "All employment statuses")] + EMPLOYMENT_STATUS_CHOICES,
        required=False,
    )
    union = forms.ChoiceField(choices=[("", "All unions")], required=False)
    verified = forms.ChoiceField(
        choices=[("", "All verification statuses"), ("yes", "Verified"), ("no", "Not verified")],
        required=False,
    )
    capture_source = forms.ChoiceField(
        choices=[("", "All capture sources")] + Worker.CAPTURE_SOURCE_CHOICES,
        required=False,
    )
    capture_mode = forms.ChoiceField(
        choices=[("", "All capture modes")] + Worker.CAPTURE_MODE_CHOICES,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        unions = list(
            TradeUnion.objects.filter(is_active=True)
            .order_by("sort_order", "name")
            .values_list("name", "name")
        )
        self.fields["union"].choices = [("", "All unions")] + unions
        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault("class", "form-input bg-white")
            else:
                field.widget.attrs.setdefault("class", "form-input")
