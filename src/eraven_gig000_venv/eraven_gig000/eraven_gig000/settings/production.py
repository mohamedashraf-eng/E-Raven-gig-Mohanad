# settings/production.py

from .base import *
import os

# Security settings
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')  # Retrieve secret key from environment variables
DEBUG = False
ALLOWED_HOSTS = ['*']

# Production database (e.g., PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', default='railway'),
        'USER': env('DB_USER', default='username'),
        'PASSWORD': env('DB_PASSWORD', default='password'),
        'HOST': env('DB_HOST', default='localhost'),
        'PORT': env('DB_PORT', default='5432'),
    }
}

# Email configuration for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='your-email@gmail.com')  # Use env variable for email
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='your-email-password')  # Use env variable for password
SERVER_EMAIL = EMAIL_HOST_USER
DEFAULT_FROM_EMAIL = f'English Path <{EMAIL_HOST_USER}>'

# Security configurations
SECURE_HSTS_SECONDS = 31536000  # HTTP Strict Transport Security
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True  # Enforce HTTPS
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Production logging (example)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/django.log'),
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'WARNING',
    },
}
