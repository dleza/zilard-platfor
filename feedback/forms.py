from django import forms

from .models import StakeholderFeedback


class StakeholderFeedbackForm(forms.ModelForm):
    class Meta:
        model = StakeholderFeedback
        fields = ["contact_name", "contact_email", "role_or_group", "page_url", "comment"]
        widgets = {
            "page_url": forms.HiddenInput(),
            "contact_name": forms.TextInput(attrs={"class": "form-input", "autocomplete": "name"}),
            "contact_email": forms.EmailInput(attrs={"class": "form-input", "autocomplete": "email"}),
            "role_or_group": forms.TextInput(attrs={"class": "form-input"}),
            "comment": forms.Textarea(attrs={"class": "form-input", "rows": 4}),
        }
