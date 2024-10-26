# ums/admin.py
from django.contrib import admin
from .models import User, Profile, Role, Permission

# Register each model with the Django admin site
admin.site.register(User)
admin.site.register(Profile)
admin.site.register(Role)
admin.site.register(Permission)
