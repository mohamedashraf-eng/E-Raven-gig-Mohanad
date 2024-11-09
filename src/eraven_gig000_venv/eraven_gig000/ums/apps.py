# ums/apps.py

from django.apps import AppConfig

class UmsConfig(AppConfig):
    name = 'ums'

    def ready(self):
        import ums.signals  # Ensure signals are imported
