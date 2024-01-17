"""
For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import os
from pathlib import Path

from django.urls import reverse_lazy

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-i&53x@=*+1)a3_!5a!q8!pxr-pm#p+bm%+s81mrq8482_a+-2_'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
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
EMAIL_HOST = 'mail.aimtravel.bg'
EMAIL_PORT = 587
EMAIL_USE_TLS = True  # Or False if not using TLS
EMAIL_HOST_USER = 'studentski@aimtravel.bg'  # Email account to send emails from
EMAIL_HOST_PASSWORD = '***'  # Password for the email account
DEFAULT_FROM_EMAIL = 'studentski@aimtravel.bg' \
                     ''  # Default sender address

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# CKEDITOR_BASEPATH = "https://cdn.ckeditor.com/4.16.0/standard/"
# CKEDITOR_UPLOAD_PATH = "uploads/"  # Define the path where uploaded files will be stored.
# CKEDITOR_CONFIGS = {
#     'default': {
#         'toolbar': 'Custom',  # You can customize the toolbar options.
#         'height': 300,  # Set the height of the CKEditor textarea.
#         'width': 800,  # Set the width of the CKEditor textarea.
#         'fillEmptyBlocks': False,  # prevent from adding extra <p> in front and behind the actual paragraph
#         'allowedContent': True,
#     },
# }


SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 1800
SESSION_SAVE_EVERY_REQUEST = True
