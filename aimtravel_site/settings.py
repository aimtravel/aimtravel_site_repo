"""
For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

import os
from pathlib import Path

from django.urls import reverse_lazy

import credentials

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = credentials.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "wkhtmltopdf",
    "django_ckeditor_5",
    "private_storage",
    "rest_framework",
    "django_vite",
    "aimtravel_site",
    "aimtravel_site.web.apps.WebConfig",
    "aimtravel_site.user_auth.apps.AccountConfig",
    "aimtravel_site.user_profile",
    "aimtravel_site.posting.apps.PostingConfig",
    "aimtravel_site.main_page.apps.MainPageConfig",
    "aimtravel_site.taxes.apps.TaxesConfig",
    "aimtravel_site.apply.apps.ApplyConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "aimtravel_site.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "aimtravel_site.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "aimtravel",
        "USER": "root",
        "PASSWORD": "mysql_pw",
        "HOST": "127.0.0.1",
        "PORT": "3306",
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = ((BASE_DIR / "static/"),)

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = reverse_lazy("sign in")
LOGIN_REDIRECT_URL = reverse_lazy("index")
LOGOUT_REDIRECT_URL = reverse_lazy("index")

AUTH_USER_MODEL = "user_auth.AppUser"
LOGIN_USERNAME_FIELDS = [
    "email",
]

DATE_INPUT_FORMATS = [
    "%d-%m-%Y",
    "%d-%m-%y",
    "%d.%m.%y",
    "%d.%m.%Y",
    "%Y-%m-%d",
    "%m/%d/%Y",
    "%m/%d/%y",
    "%b %d %Y",
    "%b %d, %Y",
    "%d %b %Y",
    "%d %b, %Y",
    "%B %d %Y",
    "%B %d, %Y",
    "%d %B %Y",
    "%d %B, %Y",
]

# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True  # Or False if not using TLS
EMAIL_HOST_USER = "stoyan.ch.stoyanov11@gmail.com"  # Email account to send emails from
EMAIL_HOST_PASSWORD = credentials.EMAILPASSWORD  # Password for the email account
DEFAULT_FROM_EMAIL = "stoyan.ch.stoyanov11@gmail.com"  # Default sender address

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

PRIVATE_STORAGE_ROOT = os.path.join(BASE_DIR, "private_media")
PRIVATE_STORAGE_AUTH_FUNCTION = (
    "aimtravel_site.taxes.views.private_storage.permissions"  # Customize permission check
)

CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": [
            "bold",
            "italic",
            "underline",
            "link",
            "fontSize",
            "fontColor",
            "fontBackgroundColor",
            "|",
            "bulletedList",
            "numberedList",
            "blockQuote",
        ],
        "height": 300,
        "width": "100%",
        "language": "bg",
        "font_size": {
            "options": [8, 10, 12, 14, 16, 18, 20, 24, 28, 32, 36],
        },
        "font_color": {
            "colors": [
                {"color": "#000000", "label": "Черен"},
                {"color": "#FF0000", "label": "Червен"},
                {"color": "#008000", "label": "Зелен"},
                {"color": "#0000FF", "label": "Син"},
                {"color": "#FFA500", "label": "Оранжев"},
            ],
        },
        # 👉 това задава черен цвят по подразбиране
        "htmlSupport": {
            "allow": [{"name": ".*", "attributes": True, "classes": True, "styles": True}]
        },
        "style": {"default": "body { color: #000000; }"},
    }
}

CKEDITOR_5_CUSTOM_CSS = "css/ckeditor_custom.css"


SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_CACHE_ALIAS = "default"
SESSION_COOKIE_AGE = 1800
SESSION_SAVE_EVERY_REQUEST = True


# ---------------------------------------------------------------------------
# "Запиши се за бригада" (aimtravel_site.apply)
#
# Local-dev configuration for the new React island. Production values (real
# Turnstile keys, Redis-backed cache, Celery broker) live in the deployment
# environment; here we keep DEBUG behavior with the anti-bot check disabled
# and Celery tasks stubbed. See handoff/docs/02-architecture.md.
# ---------------------------------------------------------------------------

# django-vite: DEBUG mode points the template tag at the Vite dev server on
# port 5173 (HMR). In production it reads static/dist/manifest.json instead.
DJANGO_VITE = {
    "default": {
        "dev_mode": DEBUG,
        "dev_server_host": "127.0.0.1",
        "dev_server_port": 5173,
        "manifest_path": BASE_DIR / "static" / "dist" / "manifest.json",
        "static_url_prefix": "dist",
    }
}

REST_FRAMEWORK = {
    "DEFAULT_THROTTLE_RATES": {
        # In DEBUG we effectively disable throttling. Draft-save has its own
        # scope (apply_draft_burst) so autosave traffic can't exhaust the
        # submit endpoint's budget before the user reaches "Изпрати".
        # Production values stay strict.
        "apply_burst": "10000/min" if DEBUG else "5/min",
        "apply_draft_burst": "10000/min" if DEBUG else "30/min",
        "apply_day": "100000/day" if DEBUG else "20/day",
        "lookup": "10000/min" if DEBUG else "120/min",
    },
}

# Cloudflare Turnstile — anti-bot on the public form. Disabled locally; real
# keys come from env vars in production.
TURNSTILE_SITE_KEY = os.environ.get("TURNSTILE_SITE_KEY", "")
TURNSTILE_SECRET_KEY = os.environ.get("TURNSTILE_SECRET_KEY", "")
TURNSTILE_DISABLED = True

# Business constants used by the apply flow (contract PDF, emails).
AIM_MANAGER_NAME = "Росен Антонов"
AIM_COMPANY_UIC = "203634922"
# In production this is "studentski@aimtravel.bg" (the studio inbox). Locally
# Gmail SMTP will reject any From that is not the authenticated account or a
# configured "send as" alias — 530 5.7.0 Authentication Required — so during
# dev we send From = EMAIL_HOST_USER instead.
AIM_FROM_EMAIL = EMAIL_HOST_USER
# Used to build absolute links (signed contract-download URL, etc). Dev-only
# value — each deployed environment patches this on the server, same as
# DEBUG/ALLOWED_HOSTS/DATABASES (see redeploy-staging skill's file-templates.md).
SITE_URL = "http://localhost:8000"

AIM_CONTRACT_TEMPLATES = os.path.join(BASE_DIR, "media", "contract_templates")
AIM_STATIC_DOCS = os.path.join(BASE_DIR, "media", "static_docs")

AIM_OFFICE_AGENTS = {
    "varna": {"name": "Стоян Стоянов", "email": "varna@aimtravel.bg", "phone": "+359 88 99 66 583"},
    "sofia": {"name": "—", "email": "sofia@aimtravel.bg", "phone": "+359 88 99 66 583"},
}
