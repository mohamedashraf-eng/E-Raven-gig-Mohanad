from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile, Role, Permission

class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active', 'total_points', 'level')
    list_filter = ('role', 'is_staff', 'is_active', 'level')
    
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'role')}),
        ('Personal Information', {
            'fields': ('profile_picture', 'phone_number', 'address', 'date_of_birth')
        }),
        ('LMS Information', {'fields': ('total_points', 'level')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'role', 'password1', 'password2', 'is_staff', 'is_active', 'profile_picture', 
                       'phone_number', 'address', 'date_of_birth', 'total_points', 'level')
        }),
    )
    
    search_fields = ('email', 'username', 'phone_number')
    ordering = ('email',)

# Register the models in the admin site
admin.site.register(User, UserAdmin)
admin.site.register(Profile)
admin.site.register(Role)
admin.site.register(Permission)
