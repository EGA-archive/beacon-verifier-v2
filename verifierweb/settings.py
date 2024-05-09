"""
Django settings for verifierweb project.

Generated by 'django-admin startproject' using Django 4.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import os
from pathlib import Path
import environ

env = environ.Env()
environ.Env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", "&nl8s430j^j8l*je+m&ys5dv#zoy)0a2+x1!m8hx290_sx&0gh")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = int(os.environ.get("DEBUG", default=1))

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "127.0.0.1").split(" ")
CSRF_TRUSTED_ORIGINS = ['https://beacon-cancer-registry-test.ega-archive.org']

STATICFILES_DIRS = [ os.path.join(PROJECT_DIR, "frontend/" )]

STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "/static/"

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, '/media')

# Application definition

INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bash',
    'crispy_forms',
    'mozilla_django_oidc',
    'channels'
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

ROOT_URLCONF = 'verifierweb.urls'

TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
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

#WSGI_APPLICATION = 'verifierweb.wsgi.application'
ASGI_APPLICATION = 'verifierweb.asgi.application'

FILES_DIR = os.path.join(BASE_DIR, "files")
# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("SQL_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.environ.get("SQL_DATABASE", os.path.join(BASE_DIR, "db.sqlite3")),
        "USER": os.environ.get("SQL_USER", "user"),
        "PASSWORD": os.environ.get("SQL_PASSWORD", "password"),
        "HOST": os.environ.get("SQL_HOST", "localhost"),
        "PORT": os.environ.get("SQL_PORT", "5432"),
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

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTHENTICATION_BACKENDS = [
'django.contrib.auth.backends.ModelBackend',
'mozilla_django_oidc.auth.OIDCAuthenticationBackend',
]

OIDC_RP_CLIENT_ID = env('OIDC_RP_CLIENT_ID')
OIDC_RP_CLIENT_SECRET = env('OIDC_RP_CLIENT_SECRET')

#OIDC_OP_AUTHORIZATION_ENDPOINT = "http://localhost:8080/auth/realms/Beacon/protocol/openid-connect/auth"
#OIDC_OP_TOKEN_ENDPOINT = "http://idp:8080/auth/realms/Beacon/protocol/openid-connect/token"
#OIDC_OP_USER_ENDPOINT = "http://idp:8080/auth/realms/Beacon/protocol/openid-connect/userinfo"

OIDC_OP_AUTHORIZATION_ENDPOINT = "https://beacon-network-demo2.ega-archive.org/auth/realms/Beacon/protocol/openid-connect/auth"
OIDC_OP_TOKEN_ENDPOINT = "https://beacon-network-demo2.ega-archive.org/auth/realms/Beacon/protocol/openid-connect/token"
OIDC_OP_USER_ENDPOINT = "https://beacon-network-demo2.ega-archive.org/auth/realms/Beacon/protocol/openid-connect/userinfo"
OIDC_STORE_ID_TOKEN = True
OIDC_OP_LOGOUT_URL_METHOD = 'my_auth.provider_logout'
OIDC_OP_LOGOUT_ENDPOINT = "https://beacon-network-demo2.ega-archive.org/auth/realms/Beacon/protocol/openid-connect/logout"

LOGIN_REDIRECT_URL = "http://localhost:8003"
LOGOUT_REDIRECT_URL = "http://localhost:8003"
#LOGIN_REDIRECT_URL = "https://beacon-test.ega-archive.org"
#LOGOUT_REDIRECT_URL = "https://beacon-test.ega-archive.org"

	
OIDC_RP_SIGN_ALGO = 'RS256'
#OIDC_OP_JWKS_ENDPOINT = 'http://idp:8080/auth/realms/Beacon/protocol/openid-connect/certs'
OIDC_OP_JWKS_ENDPOINT = 'https://beacon-network-demo2.ega-archive.org/auth/realms/Beacon/protocol/openid-connect/certs'

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER", "redis://127.0.0.1:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_BACKEND", "redis://127.0.0.1:6379/0")

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [(os.environ.get("CHANNELS_REDIS", "redis://127.0.0.1:6379/0"))],
        },
    },
}