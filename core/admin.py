from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users"""
    
    ordering = ['username']
    list_display = ['username', 'email', 'mobile', 'is_active', 'is_staff', 'date_joined']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('username', 'mobile', 'profile_type')}),
        (
            _('Permissions'),
            {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')},
        ),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'mobile', 'password1', 'password2', 'is_staff', 'is_superuser', 'profile_type'),
        }),
    )
    
    search_fields = ['email', 'username', 'mobile']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'profile_type']


# Register the User model and its admin configuration
admin.site.register(User, UserAdmin)
