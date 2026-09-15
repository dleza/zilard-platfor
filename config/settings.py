"""Django settings for the Disability-Disaggregated Labour DMIS prototype.

The defaults are intentionally simple for demos: SQLite, local media uploads,
and CDN-hosted frontend libraries. PostgreSQL can be enabled with environment
variables without changing application code.
"""
from pathlib import Path
import os

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

_INSECURE_DEFAULT_SECRET_KEY = "prototype-only-change-me"


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


DEBUG = env_bool("DJANGO_DEBUG", True)

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", _INSECURE_DEFAULT_SECRET_KEY)
if not DEBUG and SECRET_KEY == _INSECURE_DEFAULT_SECRET_KEY:
    # The placeholder key is fine for local prototype demos (DEBUG=True) but must
    # never be used once DEBUG is off — fail loudly instead of silently shipping
    # a well-known secret key.
    raise ImproperlyConfigured(
        "DJANGO_SECRET_KEY must be set to a real secret when DJANGO_DEBUG is not enabled."
    )

if DEBUG and not os.getenv("DJANGO_ALLOWED_HOSTS"):
    ALLOWED_HOSTS = ["127.0.0.1", "localhost", "0.0.0.0", "*"]
else:
    ALLOWED_HOSTS = [
        host.strip()
        for host in os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")
        if host.strip()
    ]
    if not DEBUG and ALLOWED_HOSTS == ["127.0.0.1", "localhost"] and not os.getenv("DJANGO_ALLOWED_HOSTS"):
        # Same idea as SECRET_KEY above: don't let a real deployment run on the
        # local-only default without someone explicitly deciding on its hosts.
        raise ImproperlyConfigured(
            "DJANGO_ALLOWED_HOSTS must be set explicitly when DJANGO_DEBUG is not enabled."
        )

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "core.apps.CoreConfig",
    "website.apps.WebsiteConfig",
    "mobile_api.apps.MobileApiConfig",
    "users.apps.UsersConfig",
    "workers.apps.WorkersConfig",
    "monitoring.apps.MonitoringConfig",
    "dashboards.apps.DashboardsConfig",
    "reports.apps.ReportsConfig",
    "feedback.apps.FeedbackConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "core.middleware.MobileApiCorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "core.middleware.CurrentUserMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.prototype_context",
                "feedback.context_processors.feedback_form",
                "website.context_processors.site_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

if os.getenv("DB_ENGINE", "sqlite").lower() in {"postgres", "postgresql"}:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB", "dldms"),
            "USER": os.getenv("POSTGRES_USER", "dldms"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", ""),
            "HOST": os.getenv("POSTGRES_HOST", "127.0.0.1"),
            "PORT": os.getenv("POSTGRES_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_USER_MODEL = "users.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en"
TIME_ZONE = os.getenv("DJANGO_TIME_ZONE", "Africa/Lusaka")
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "users:login"
LOGIN_REDIRECT_URL = "dashboards:home"
LOGOUT_REDIRECT_URL = "users:login"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 50,
}

DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
