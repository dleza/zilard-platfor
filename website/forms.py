from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    # Honeypot: real visitors never see or fill this field (hidden via CSS).
    # Any bot that fills it gets silently dropped in the view.
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "organisation", "category", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "field-input", "autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"class": "field-input", "autocomplete": "email"}),
            "organisation": forms.TextInput(attrs={"class": "field-input", "autocomplete": "organization"}),
            "category": forms.Select(attrs={"class": "field-input"}),
            "message": forms.Textarea(attrs={"class": "field-input", "rows": 6}),
        }
        labels = {
            "organisation": "Organisation (optional)",
        }

    def clean_website(self):
        value = self.cleaned_data.get("website")
        if value:
            raise forms.ValidationError("Spam detected.")
        return value
