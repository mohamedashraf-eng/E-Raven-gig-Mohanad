#!/bin/bash

# Install dependencies
pip3 install -r requirements.txt

# Set environment variables
export DJANGO_SETTINGS_MODULE="eraven_gig000.settings.development"  # Update with actual settings module for production
export DJANGO_SECRET_KEY="${DJANGO_SECRET_KEY:-mowx}"  # Set this securely in Render's environment variables

# Collect static files
python3 manage.py collectstatic --noinput

# Apply database migrations
python3 manage.py makemigrations --noinput
python3 manage.py migrate --noinput

# Create a superuser if it does not exist
python3 manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username="eraven").exists():
    User.objects.create_superuser("eraven", "eraven@gmail.com", "eraven")
END

# Start the Gunicorn server on port 8000
exec gunicorn eraven_gig000.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile '-' \
    --error-logfile '-' \
    --log-level info
