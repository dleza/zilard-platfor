from django import forms

from .choices import DISABILITY_TYPE_CHOICES, GROUPED_DISTRICT_CHOICES, PROVINCE_CHOICES
from .models import DisabilityProfile, LabourRightsRecord, Occupation, TradeUnion, Worker, WorkerDocument, Workplace


class OccupationChoiceMixin:
    def apply_occupation_choices(self):
        if "occupation" not in self.fields:
            return

        occupations = list(
            Occupation.objects.filter(is_active=True)
            .order_by("sort_order", "name")
            .values_list("name", "name")
        )
        current_value = self.initial.get("occupation") or getattr(self.instance, "occupation", "")
        if current_value and current_value not in {value for value, _label in occupations}:
            occupations.insert(0, (current_value, f"{current_value} (existing value)"))

        self.fields["occupation"] = forms.ChoiceField(
            label=self.fields["occupation"].label,
            required=False,
            choices=[("", "Select occupation")] + occupations,
            help_text="Manage the selectable occupation list in Django Admin under Occupation settings.",
            widget=forms.Select(),
        )


class TradeUnionChoiceMixin:
    def active_union_choices(self, current_value="", empty_label="Select union"):
        unions = list(
            TradeUnion.objects.filter(is_active=True)
            .order_by("sort_order", "name")
            .values_list("name", "name")
        )
        if current_value and current_value not in {value for value, _label in unions}:
            unions.insert(0, (current_value, f"{current_value} (existing value)"))
        return [("", empty_label)] + unions

    def apply_trade_union_choices(self):
        if "union_name" not in self.fields:
            return

        current_value = self.initial.get("union_name") or getattr(self.instance, "union_name", "")
        self.fields["union_name"] = forms.ChoiceField(
            label=self.fields["union_name"].label,
            required=False,
            choices=self.active_union_choices(current_value=current_value),
            help_text="Manage the selectable union list in Django Admin under Trade union settings.",
            widget=forms.Select(),
        )


class TailwindFormMixin:
    text_class = "form-input"
    checkbox_class = "h-5 w-5 rounded border-slate-300 text-emerald-700 focus:ring-emerald-600"

    def apply_tailwind(self):
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault("class", self.checkbox_class)
            elif isinstance(widget, forms.Select):
                widget.attrs.setdefault("class", "form-input bg-white")
            elif isinstance(widget, forms.FileInput):
                widget.attrs.setdefault("class", "block w-full text-sm text-slate-700 file:mr-4 file:rounded-md file:border-0 file:bg-emerald-50 file:px-4 file:py-2 file:text-emerald-800 hover:file:bg-emerald-100")
            else:
                widget.attrs.setdefault("class", self.text_class)


class WorkerBaseForm(OccupationChoiceMixin, TradeUnionChoiceMixin, forms.ModelForm):
    class Meta:
        model = Worker
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_occupation_choices()
        self.apply_trade_union_choices()


class WorkerForm(TailwindFormMixin, OccupationChoiceMixin, TradeUnionChoiceMixin, forms.ModelForm):
    class Meta:
        model = Worker
        fields = [
            "first_name",
            "last_name",
            "other_names",
            "national_id",
            "nationality",
            "gender",
            "date_of_birth",
            "phone",
            "email",
            "province",
            "district",
            "workplace",
            "sector",
            "occupation",
            "employment_status",
            "union_membership_status",
            "union_name",
            "leadership_participation",
            "committee_participation",
            "organising_activities",
            "latitude",
            "longitude",
            "photo",
            "consent_to_store_data",
            "data_verified",
        ]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "province": forms.Select(attrs={"data-province-select": "true"}),
            "district": forms.Select(attrs={"data-district-select": "true"}),
            "organising_activities": forms.Textarea(attrs={"rows": 3}),
            "latitude": forms.NumberInput(attrs={"step": "0.000001", "data-gps-lat": "true"}),
            "longitude": forms.NumberInput(attrs={"step": "0.000001", "data-gps-lng": "true"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_occupation_choices()
        self.apply_trade_union_choices()
        self.apply_tailwind()


class DisabilityProfileForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = DisabilityProfile
        exclude = ["worker"]
        widgets = {
            "assistive_devices": forms.Textarea(attrs={"rows": 3}),
            "accommodation_requirements": forms.Textarea(attrs={"rows": 3}),
            "accessibility_challenges": forms.Textarea(attrs={"rows": 3}),
            "functional_limitations": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_tailwind()


class LabourRightsRecordForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = LabourRightsRecord
        exclude = ["worker"]
        widgets = {"grievance_summary": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_tailwind()


class WorkerDocumentForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = WorkerDocument
        fields = ["title", "document_type", "file"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].required = False
        self.fields["file"].required = False
        self.apply_tailwind()


class WorkplaceForm(TailwindFormMixin, forms.ModelForm):
    accommodations_available = forms.TypedChoiceField(
        label="Accommodations available",
        choices=(("yes", "Yes"), ("no", "No")),
        coerce=lambda value: value == "yes",
        widget=forms.Select(),
    )

    class Meta:
        model = Workplace
        fields = [
            "employer_name",
            "workplace_name",
            "province",
            "district",
            "address",
            "sector",
            "latitude",
            "longitude",
            "accessibility_status",
            "accommodations_available",
            "union_presence",
            "notes",
        ]
        widgets = {
            "province": forms.Select(attrs={"data-province-select": "true"}),
            "district": forms.Select(attrs={"data-district-select": "true"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
            "latitude": forms.NumberInput(attrs={"step": "0.000001", "data-gps-lat": "true"}),
            "longitude": forms.NumberInput(attrs={"step": "0.000001", "data-gps-lng": "true"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound:
            self.fields["accommodations_available"].initial = (
                "yes" if self.instance and self.instance.accommodations_available else "no"
            )
        self.apply_tailwind()


class WorkplaceAdminForm(WorkplaceForm):
    class Meta(WorkplaceForm.Meta):
        fields = "__all__"


class WorkerFilterForm(TailwindFormMixin, TradeUnionChoiceMixin, forms.Form):
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
    disability_type = forms.ChoiceField(choices=[("", "All disability types")] + DISABILITY_TYPE_CHOICES, required=False)
    union = forms.ChoiceField(choices=[("", "All unions")], required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["union"].choices = self.active_union_choices(empty_label="All unions")
        self.apply_tailwind()


class OccupationForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Occupation
        fields = ["name", "sector", "description", "is_active", "sort_order"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_tailwind()


class TradeUnionForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = TradeUnion
        fields = ["name", "full_name", "description", "is_active", "sort_order"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_tailwind()
