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
    'localhost',
    '127.0.0.1',
    'testpetar.aimtravel.bg',
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'wkhtmltopdf',
    'django_ckeditor_5',
    'private_storage',

    'aimtravel_site',

    'aimtravel_site.web.apps.WebConfig',
    'aimtravel_site.user_auth.apps.AccountConfig',
    'aimtravel_site.user_profile',
    'aimtravel_site.posting.apps.PostingConfig',
    'aimtravel_site.main_page.apps.MainPageConfig',
    'aimtravel_site.taxes.apps.TaxesConfig',
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
        'DIRS': [BASE_DIR / 'templates', ],
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
        'NAME': 'aimtravel',
        'USER': 'root',
        'PASSWORD': 'mysql_pw',
        'HOST': '127.0.0.1',
        'PORT': '3306',
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

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = (BASE_DIR / 'static/'),

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
    '%d.%m.%Y',
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
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True  # Or False if not using TLS
EMAIL_HOST_USER = 'vlzahariev26@gmail.com'  # Email account to send emails from
EMAIL_HOST_PASSWORD = credentials.EMAILPASSWORD  # Password for the email account
DEFAULT_FROM_EMAIL = 'vlzahariev26@gmail.com' \
                     ''  # Default sender address

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

PRIVATE_STORAGE_ROOT = os.path.join(BASE_DIR, 'private_media')
PRIVATE_STORAGE_AUTH_FUNCTION = 'aimtravel_site.taxes.views.private_storage.permissions'   # Customize permission check

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





SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 1800
SESSION_SAVE_EVERY_REQUEST = True
