from django import forms
from django.contrib.auth.forms import AuthenticationForm

from workers.models import TradeUnion

from .models import User, UserCategory


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
            else:
                widget.attrs.setdefault("class", self.text_class)


class AccessibleAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"autocomplete": "username", "class": "form-input", "autofocus": True})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password", "class": "form-input"})
    )


class OTPForm(forms.Form):
    code = forms.CharField(
        label="Authenticator code",
        min_length=6,
        max_length=6,
        widget=forms.TextInput(
            attrs={
                "inputmode": "numeric",
                "autocomplete": "one-time-code",
                "class": "form-input text-center text-2xl tracking-widest",
            }
        ),
    )


class TOTPDisableForm(forms.Form):
    """Requires the user to re-enter their password before turning 2FA off."""

    password = forms.CharField(
        label="Current password",
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password", "class": "form-input"}),
    )

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data["password"]
        if not self.user or not self.user.check_password(password):
            raise forms.ValidationError("That password is incorrect.")
        return password


class UserManagementForm(TailwindFormMixin, forms.ModelForm):
    password1 = forms.CharField(
        label="Password",
        required=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text="Required for new users. Leave blank when editing to keep the existing password.",
    )
    password2 = forms.CharField(
        label="Confirm password",
        required=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "assigned_union",
            "phone",
            "organisation",
            "is_active",
            "is_staff",
        ]
        widgets = {
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        active_roles = list(
            UserCategory.objects.filter(is_active=True)
            .order_by("sort_order", "display_name")
            .values_list("role", "display_name")
        )
        current_role = self.initial.get("role") or getattr(self.instance, "role", "")
        if current_role and current_role not in {value for value, _label in active_roles}:
            active_roles.insert(0, (current_role, f"{self.instance.get_role_display()} (existing value)"))
        self.fields["role"].choices = active_roles or User.ROLE_CHOICES

        unions = list(
            TradeUnion.objects.filter(is_active=True)
            .order_by("sort_order", "name")
            .values_list("name", "name")
        )
        current_union = self.initial.get("assigned_union") or getattr(self.instance, "assigned_union", "")
        if current_union and current_union not in {value for value, _label in unions}:
            unions.insert(0, (current_union, f"{current_union} (existing value)"))
        self.fields["assigned_union"] = forms.ChoiceField(
            required=False,
            choices=[("", "No union restriction")] + unions,
            help_text="Use for Trade Union Focal Person and Data Collector accounts that should only see one union.",
        )

        if not self.instance.pk:
            self.fields["password1"].required = True
            self.fields["password2"].required = True
        self.apply_tailwind()

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 or password2:
            if password1 != password2:
                raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password1")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


class UserCategoryForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = UserCategory
        fields = ["role", "display_name", "description", "is_active", "sort_order"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        existing_roles = set(
            UserCategory.objects.exclude(pk=self.instance.pk if self.instance else None).values_list("role", flat=True)
        )
        self.fields["role"].choices = [
            (value, label)
            for value, label in User.ROLE_CHOICES
            if value not in existing_roles or value == getattr(self.instance, "role", "")
        ]
        self.apply_tailwind()
