from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LogoutView
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView

from .forms import AccessibleAuthenticationForm, OTPForm, TOTPDisableForm, UserCategoryForm, UserManagementForm
from .models import User, UserCategory
from .totp import generate_secret, provisioning_uri, verify_totp


class SystemAdminRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("users:login")
        if not getattr(request.user, "is_system_admin", False):
            raise PermissionDenied("Only system administrators can access settings.")
        return super().dispatch(request, *args, **kwargs)


class LoginView(View):
    template_name = "registration/login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("dashboards:home")
        return render(request, self.template_name, {"form": AccessibleAuthenticationForm(request)})

    def post(self, request):
        form = AccessibleAuthenticationForm(request, data=request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form}, status=400)

        user = form.get_user()
        if user.totp_enabled:
            request.session["pending_2fa_user_id"] = user.pk
            return redirect("users:verify-otp")

        login(request, user)
        return redirect("dashboards:home")


class VerifyOTPView(View):
    template_name = "registration/verify_otp.html"

    def get_pending_user(self, request):
        user_id = request.session.get("pending_2fa_user_id")
        if not user_id:
            return None
        try:
            return User.objects.get(pk=user_id, is_active=True)
        except User.DoesNotExist:
            return None

    def get(self, request):
        user = self.get_pending_user(request)
        if not user:
            return redirect("users:login")
        return render(request, self.template_name, {"form": OTPForm(), "pending_user": user})

    def post(self, request):
        user = self.get_pending_user(request)
        if not user:
            return redirect("users:login")

        form = OTPForm(request.POST)
        if form.is_valid() and verify_totp(user.totp_secret, form.cleaned_data["code"]):
            request.session.pop("pending_2fa_user_id", None)
            login(request, user)
            return redirect("dashboards:home")

        messages.error(request, "The authenticator code was not accepted.")
        return render(request, self.template_name, {"form": form, "pending_user": user}, status=400)


class SignOutView(LogoutView):
    next_page = reverse_lazy("users:login")


class TOTPSetupView(View):
    """Self-service enrollment: the logged-in user scans a QR code to turn on 2FA.

    A pending (unconfirmed) secret is held in the session, never saved to the user
    record, until the user proves they can generate a valid code with it. This is
    the only way `totp_enabled`/`totp_secret` get set for a user going forward, so
    nobody is ever locked out by an admin flipping a checkbox on their behalf.
    """

    template_name = "registration/totp_setup.html"
    session_key = "totp_pending_secret"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("users:login")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        if request.user.totp_enabled:
            return render(
                request,
                self.template_name,
                {"enabled": True, "disable_form": TOTPDisableForm(user=request.user)},
            )

        secret = request.session.get(self.session_key)
        if not secret:
            secret = generate_secret()
            request.session[self.session_key] = secret

        uri = provisioning_uri(secret, request.user.username)
        return render(
            request,
            self.template_name,
            {
                "enabled": False,
                "secret": secret,
                "provisioning_uri": uri,
                "form": OTPForm(),
            },
        )

    def post(self, request):
        if request.user.totp_enabled:
            return redirect("users:totp-setup")

        secret = request.session.get(self.session_key)
        if not secret:
            messages.error(request, "Your setup session expired. Start again.")
            return redirect("users:totp-setup")

        form = OTPForm(request.POST)
        if form.is_valid() and verify_totp(secret, form.cleaned_data["code"]):
            request.user.totp_secret = secret
            request.user.totp_enabled = True
            request.user.save(update_fields=["totp_secret", "totp_enabled"])
            request.session.pop(self.session_key, None)
            messages.success(request, "Two-factor authentication is now enabled on your account.")
            return redirect("users:totp-setup")

        messages.error(request, "That code didn't match. Scan the QR code again and try the current 6-digit code.")
        uri = provisioning_uri(secret, request.user.username)
        return render(
            request,
            self.template_name,
            {"enabled": False, "secret": secret, "provisioning_uri": uri, "form": form},
            status=400,
        )


class TOTPDisableView(View):
    """Self-service: the user re-enters their password to turn 2FA back off."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("users:login")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        form = TOTPDisableForm(request.POST, user=request.user)
        if form.is_valid():
            request.user.totp_enabled = False
            request.user.totp_secret = ""
            request.user.save(update_fields=["totp_enabled", "totp_secret"])
            messages.success(request, "Two-factor authentication has been turned off.")
        else:
            error_detail = " ".join(form.errors.get("password", [])) or "Incorrect password."
            messages.error(request, f"Couldn't turn off 2FA: {error_detail}")
        return redirect("users:totp-setup")


class SettingsTOTPResetView(SystemAdminRequiredMixin, View):
    """Admin action: clear a locked-out user's 2FA so they can re-enroll themselves.

    This cannot turn 2FA *on* for someone else — only off — which is what keeps
    self-enrollment the single source of truth for the secret an authenticator app holds.
    """

    def post(self, request, pk):
        managed_user = get_object_or_404(User, pk=pk)
        managed_user.totp_enabled = False
        managed_user.totp_secret = ""
        managed_user.save(update_fields=["totp_enabled", "totp_secret"])
        messages.success(request, f"2FA reset for {managed_user.username}. They can re-enroll from their own account.")
        return redirect("workers:settings-user-edit", pk=managed_user.pk)


class SettingsUserListView(SystemAdminRequiredMixin, ListView):
    model = User
    template_name = "settings/user_list.html"
    context_object_name = "managed_users"
    paginate_by = 25

    def get_queryset(self):
        queryset = User.objects.all().order_by("username")
        q = self.request.GET.get("q")
        role = self.request.GET.get("role")
        if q:
            queryset = queryset.filter(
                Q(username__icontains=q)
                | Q(first_name__icontains=q)
                | Q(last_name__icontains=q)
                | Q(email__icontains=q)
                | Q(organisation__icontains=q)
                | Q(assigned_union__icontains=q)
            )
        if role:
            queryset = queryset.filter(role=role)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_categories"] = UserCategory.objects.order_by("sort_order", "display_name")
        return context


class SettingsUserFormView(SystemAdminRequiredMixin, View):
    template_name = "settings/user_form.html"
    user_instance = None

    def dispatch(self, request, *args, **kwargs):
        if "pk" in kwargs:
            self.user_instance = get_object_or_404(User, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(
            request,
            self.template_name,
            {
                "form": UserManagementForm(instance=self.user_instance),
                "managed_user": self.user_instance,
                "title": "Edit User" if self.user_instance else "Add User",
            },
        )

    def post(self, request, *args, **kwargs):
        form = UserManagementForm(request.POST, instance=self.user_instance)
        if form.is_valid():
            form.save()
            messages.success(request, "User account saved.")
            return redirect("workers:settings-users")
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "managed_user": self.user_instance,
                "title": "Edit User" if self.user_instance else "Add User",
            },
            status=400,
        )


class SettingsUserCategoryListView(SystemAdminRequiredMixin, ListView):
    model = UserCategory
    template_name = "settings/user_category_list.html"
    context_object_name = "user_categories"
    paginate_by = 25

    def get_queryset(self):
        queryset = UserCategory.objects.all()
        q = self.request.GET.get("q")
        if q:
            queryset = queryset.filter(Q(display_name__icontains=q) | Q(description__icontains=q) | Q(role__icontains=q))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        configured_roles = set(UserCategory.objects.values_list("role", flat=True))
        context["can_add_category"] = any(role not in configured_roles for role, _label in User.ROLE_CHOICES)
        return context


class SettingsUserCategoryFormView(SystemAdminRequiredMixin, View):
    template_name = "settings/user_category_form.html"
    category = None

    def dispatch(self, request, *args, **kwargs):
        if "pk" in kwargs:
            self.category = get_object_or_404(UserCategory, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(
            request,
            self.template_name,
            {
                "form": UserCategoryForm(instance=self.category),
                "category": self.category,
                "title": "Edit User Category" if self.category else "Add User Category",
            },
        )

    def post(self, request, *args, **kwargs):
        form = UserCategoryForm(request.POST, instance=self.category)
        if form.is_valid():
            form.save()
            messages.success(request, "User category saved.")
            return redirect("workers:settings-user-categories")
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "category": self.category,
                "title": "Edit User Category" if self.category else "Add User Category",
            },
            status=400,
        )
