# settings/development.py

from .base import *

# Security settings
SECRET_KEY = 'django-insecure-kdvo2(v#+hz8!lb(gx@ju($@&dncgq*i=*$$&=8k7l^0rv$j85'  # Replace with a more secure key in production
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Database configuration (development)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Development logging
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
