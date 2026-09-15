from django.urls import path

from .views import (
    LoginView,
    SettingsTOTPResetView,
    SignOutView,
    TOTPDisableView,
    TOTPSetupView,
    VerifyOTPView,
)

app_name = "users"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
    path("logout/", SignOutView.as_view(), name="logout"),
    path("2fa/", TOTPSetupView.as_view(), name="totp-setup"),
    path("2fa/disable/", TOTPDisableView.as_view(), name="totp-disable"),
    path("2fa/reset/<int:pk>/", SettingsTOTPResetView.as_view(), name="settings-totp-reset"),
]
