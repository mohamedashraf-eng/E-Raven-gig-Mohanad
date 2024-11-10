# settings/base.py

from pathlib import Path
import os
from datetime import timedelta
import environ

# Initialize environment variables
env = environ.Env()
environ.Env.read_env()

# Base Directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
# Define the URL to redirect unauthenticated users
LOGIN_URL = '/api/v1/sign-in'  # Replace with your desired URL

# Optionally, define a `LOGIN_REDIRECT_URL` for post-login redirection
LOGIN_REDIRECT_URL = 'api/v1/user-profile/'  # Replace as needed

# Installed Applications
INSTALLED_APPS = [
    # Django Apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party apps
    # 'django_bootstrap5',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework.authtoken',
    'crispy_forms',
    'django_extensions',
    # 'ratelimit',  # Uncomment if rate limiting is needed

    # Custom Apps
    'pages.apps.PagesConfig',
    'ums.apps.UmsConfig',
    'cms.apps.CmsConfig',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'ums.middleware.JWTAuthenticationMiddleware', 
]

# URL Configuration
ROOT_URLCONF = 'eraven_gig000.urls'
WSGI_APPLICATION = 'eraven_gig000.wsgi.application'

# Template Configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

# Custom User Model
AUTH_USER_MODEL = 'ums.User'

# Authentication and Authorization
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'ums.authentication.CookieJWTAuthentication',  # Custom authentication for JWT cookies
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# JWT Settings for Authentication
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'SIGNING_KEY': 'mowx',  # Use your project's secret key from environment
    'ALGORITHM': 'HS256',
    'AUTH_COOKIE': 'access_token',  # Name of the access token cookie
    'AUTH_COOKIE_REFRESH': 'refresh_token',  # Name of the refresh token cookie
    'AUTH_COOKIE_SECURE': False,  # Set to True in production
    'AUTH_COOKIE_HTTP_ONLY': True,
    'AUTH_COOKIE_SAMESITE': 'Lax',  # Adjust as needed
}

# Password Validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization and Localization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static and Media Files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'eraven_gig000/static')]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default Primary Key Field Type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
