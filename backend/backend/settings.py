"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 5.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
from pathlib import Path

from django.utils.timezone import timedelta
from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    
    "rest_framework",
    "rest_framework.authtoken",
    "djoser",
    "social_django",
    "corsheaders",
    "rest_framework_simplejwt",
    "django_filters",
    
    "backend.apps.healthcheck",
    "backend.apps.shared",
    "backend.apps.users",
    "backend.apps.company",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "social_django.middleware.SocialAuthExceptionMiddleware",
]

ROOT_URLCONF = "backend.backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
            ],
        },
    },
]

WSGI_APPLICATION = "backend.backend.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.getenv("DB_HOST", "database"),
        "NAME": os.getenv("DB_NAME", "postgres"),
        "USER": os.getenv("DB_USER", "postgres"),
        "PASSWORD": os.getenv("DB_PASSWORD", "pass"),
    },
    "test": {
        "NAME": f"test_{os.getenv('DB_NAME', 'postgres')}",
    },
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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

AUTH_USER_MODEL = "users.CustomUser"

# EMAIL CONFIGURATION

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = os.getenv("EMAIL_PORT", default="587")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True

# LOGGING

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "level": "WARNING",
            "class": "logging.FileHandler",
            "filename": "logs/file_logs/mailing.log",
            "formatter": "verbose",
        },
        "rotating_file": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/rotating_logs/mailing.log",
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 5,
            "formatter": "verbose",
        },
        "db_operations": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "logs/db_operations/db_operations.log",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "mailing": {
            "handlers": ["file"],
            "level": "WARNING",
            "propagate": True,
        },
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
        "django.request": {
            "handlers": ["console", "rotating_file"],
            "level": "ERROR",
            "propagate": False,
        },
        "db_operations": {
            "handlers": ["db_operations"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

LANGUAGES = [
    ("en", _("English")),
    ("uk", _("Ukrainian")),
]

LOCALE_PATHS = [
    BASE_DIR / "locale",
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"

# MEDIA

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# DRF

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# DJOSER SETTINGS

DJOSER = {
    "USER_CREATE_PASSWORD_RETYPE": True,
    "USERNAME_CHANGED_EMAIL_CONFIRMATION": True,
    "PASSWORD_CHANGED_EMAIL_CONFIRMATION": True,
    "SEND_CONFIRMATION_EMAIL": True,
    "SET_PASSWORD_RETYPE": True,
    "PASSWORD_RESET_CONFIRM_URL": "password/reset/confirm/{uid}/{token}",
    "ACTIVATION_URL": "activate/{uid}/{token}",
    "SEND_ACTIVATION_EMAIL": True,
    "SOCIAL_AUTH_TOKEN_STRATEGY": "djoser.social.token.jwt.TokenStrategy",
    "SOCIAL_AUTH_ALLOWED_REDIRECT_URIS": ["http://localhost:3000"],
    "SERIALIZERS": {
        "user_create": "backend.apps.users.serializers.UserSerializer",
        "user": "backend.apps.users.serializers.UserSerializer",
        "current_user": "backend.apps.users.serializers.UserSerializer",
        "user_delete": "djoser.serializers.UserDeleteSerializer",
    },
    "EMAIL": {
        "activation": "backend.apps.users.email.ActivationEmail",
        "confirmation": "backend.apps.users.email.ConfirmationEmail",
        "password_reset": "backend.apps.users.email.PasswordResetEmail",
        "password_changed_confirmation": "backend.apps.users.email.PasswordChangedConfirmationEmail",
    },
}

# SOCIAL AUTH

SOCIAL_AUTH_JSONFIELD_ENABLED = True

AUTHENTICATION_BACKENDS = (
    "social_core.backends.github.GithubOAuth2",
    "django.contrib.auth.backends.ModelBackend",
)

SOCIAL_AUTH_REDIRECT_IS_HTTPS = False
SOCIAL_AUTH_GITHUB_KEY = os.getenv("SOCIAL_AUTH_GITHUB_KEY")
SOCIAL_AUTH_GITHUB_SECRET = os.getenv("SOCIAL_AUTH_GITHUB_SECRET")

# CORS

CORS_ALLOW_ALL_ORIGINS = True
