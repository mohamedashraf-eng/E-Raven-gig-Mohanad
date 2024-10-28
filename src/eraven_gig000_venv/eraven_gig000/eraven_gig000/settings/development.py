# settings/development.py

from .base import *
import environ
import os

# Initialize environment variables
env = environ.Env(
    DEBUG=(bool, False)  # Set casting and default value
)

# Read .env file
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Security settings
SECRET_KEY = env('SECRET_KEY', default='django-insecure-default-key')  # Use env variable for production key
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Database configuration for development (SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Email backend configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='your-email@gmail.com')  # Use env variable for email
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='your-email-password')  # Use env variable for password
SERVER_EMAIL = EMAIL_HOST_USER
DEFAULT_FROM_EMAIL = f'English Path <{EMAIL_HOST_USER}>'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}