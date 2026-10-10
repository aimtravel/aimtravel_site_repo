"""
For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/

This is production's settings.py (aimtravel.bg, 2026-10-07) with its secrets
moved out: they are read from credentials.py, a server-only file that is never
committed (see the PR description for the keys it must define). The other
environment-specific values below default to production's values and can be
overridden in credentials.py for local development.
"""
import os
from pathlib import Path

from django.urls import reverse_lazy
from decouple import config

import credentials

GOOGLE_SHEETS_WEBHOOK_URL = os.environ.get('GOOGLE_SHEETS_WEBHOOK_URL', '')
GOOGLE_SHEETS_WEBHOOK_SECRET = os.environ.get('GOOGLE_SHEETS_WEBHOOK_SECRET', '')

try:
    from wat_credentials import (
        GOOGLE_SHEETS_WEBHOOK_SECRET as _WAT_SHEETS_SECRET,
        GOOGLE_SHEETS_WEBHOOK_URL as _WAT_SHEETS_URL,
    )
except ImportError:
    pass
else:
    if not GOOGLE_SHEETS_WEBHOOK_URL:
        GOOGLE_SHEETS_WEBHOOK_URL = _WAT_SHEETS_URL
    if not GOOGLE_SHEETS_WEBHOOK_SECRET:
        GOOGLE_SHEETS_WEBHOOK_SECRET = _WAT_SHEETS_SECRET

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = credentials.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = getattr(credentials, 'DEBUG', False)

ALLOWED_HOSTS = getattr(
    credentials, 'ALLOWED_HOSTS',
    ['aimtravel.bg', 'www.aimtravel.bg', 'https://www.aimtravel.bg', 'https://aimtravel.bg'],
)

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_social_share',
    'django_ckeditor_5',

    'aimtravel_site.web.apps.WebConfig',
    'aimtravel_site.user_auth',
    'aimtravel_site.user_profile',
    'aimtravel_site.posting.apps.PostingConfig',
    'aimtravel_site.main_page',
    'aimtravel_site.taxes'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'aimtravel_site.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates',]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

            ],
        },
    },
]

WSGI_APPLICATION = 'aimtravel_site.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': credentials.DB_NAME,
        'USER': credentials.DB_USER,
        'PASSWORD': credentials.DB_PASSWORD,
        'HOST': getattr(credentials, 'DB_HOST', 'localhost'),
        'PORT': getattr(credentials, 'DB_PORT', '3306'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATICFILES_DIRS = getattr(credentials, 'STATICFILES_DIRS', ['/home/aimtrave/public_html/assets', ])
STATIC_ROOT = getattr(credentials, 'STATIC_ROOT', '/home/aimtrave/public_html/static')
MEDIA_ROOT = getattr(credentials, 'MEDIA_ROOT', '/home/aimtrave/public_html/media')

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = reverse_lazy('sign in')
LOGIN_REDIRECT_URL = reverse_lazy('index')
LOGOUT_REDIRECT_URL = reverse_lazy('index')

AUTH_USER_MODEL = 'user_auth.AppUser'
LOGIN_USERNAME_FIELDS = ['email', ]

DATE_INPUT_FORMATS = [
    '%d-%m-%Y',
    '%d-%m-%y',
    '%d.%m.%y',
    '%Y-%m-%d',
    '%m/%d/%Y',
    '%m/%d/%y',
    '%b %d %Y',
    '%b %d, %Y',
    '%d %b %Y',
    '%d %b, %Y',
    '%B %d %Y',
    '%B %d, %Y',
    '%d %B %Y',
    '%d %B, %Y']

# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND = getattr(credentials, 'EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = 'mail.aimtravel.bg'
EMAIL_PORT = 587
EMAIL_USE_TLS = True  # Or False if not using TLS
EMAIL_HOST_USER = credentials.EMAIL_HOST_USER  # Email account to send emails from
EMAIL_HOST_PASSWORD = credentials.EMAILPASSWORD  # Password for the email account
DEFAULT_FROM_EMAIL = 'studentski@aimtravel.bg' \
                     ''  # Default sender address

CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': [
            'bold', 'italic', 'underline', 'link',
            'fontSize', 'fontColor', 'fontBackgroundColor',
            '|', 'bulletedList', 'numberedList', 'blockQuote',
        ],
        'height': 300,
        'width': '100%',
        'language': 'bg',
        'font_size': {
            'options': [8, 10, 12, 14, 16, 18, 20, 24, 28, 32, 36],
        },
        'font_color': {
            'colors': [
                {'color': '#000000', 'label': 'Черен'},
                {'color': '#FF0000', 'label': 'Червен'},
                {'color': '#008000', 'label': 'Зелен'},
                {'color': '#0000FF', 'label': 'Син'},
                {'color': '#FFA500', 'label': 'Оранжев'},
            ],
        },
        # 👉 това задава черен цвят по подразбиране
        'htmlSupport': {
            'allow': [
                {'name': '.*', 'attributes': True, 'classes': True, 'styles': True}
            ]
        },
        'style': {
            'default': 'body { color: #000000; }'
        }
    }
}

CKEDITOR_5_CUSTOM_CSS = 'css/ckeditor_custom.css'
