# settings/base.py

from pathlib import Path
import os
from datetime import timedelta
import environ
from django.contrib.messages import constants as message_constants

# Initialize environment variables
env = environ.Env()
environ.Env.read_env()

# Base Directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
# Define the URL to redirect unauthenticated users
LOGIN_URL = '/api/v1/sign-in'  # Replace with your desired URL

# Optionally, define a `LOGIN_REDIRECT_URL` for post-login redirection
LOGIN_REDIRECT_URL = 'api/v1/user-profile/'  # Replace as needed

# Fetch values from environment variables
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')

PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID')
PAYPAL_CLIENT_SECRET = os.getenv('PAYPAL_CLIENT_SECRET')

SITE_URL = os.getenv('SITE_URL', 'http://localhost:8000')  # Default to localhost if not set

PAYMOB_API_KEY = os.getenv('PAYMOB_API_KEY', '')
PAYMOB_INTEGRATION_ID = os.getenv('PAYMOB_INTEGRATION_ID', '')
PAYMOB_USERNAME = os.getenv('PAYMOB_USERNAME', '')
PAYMOB_PASSWORD = os.getenv('PAYMOB_PASSWORD', '')
PAYMOB_IFRAME_ID = os.getenv('PAYMOB_IFRAME_ID', '')

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
    'products.apps.ProductsConfig',
    'orders.apps.OrdersConfig',
    'payments.apps.PaymentsConfig',
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


MESSAGE_TAGS = {
    message_constants.DEBUG: 'secondary',
    message_constants.INFO: 'info',
    message_constants.SUCCESS: 'success',
    message_constants.WARNING: 'warning',
    message_constants.ERROR: 'danger',
}

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
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
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
