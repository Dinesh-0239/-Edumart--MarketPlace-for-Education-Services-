from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    """Custom admin panel configuration for CustomUser model."""
    
    model = CustomUser
    list_display = ('username', 'email', 'is_service_provider', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email')
    list_filter = ('is_service_provider', 'is_staff', 'is_active', 'date_joined')
    
    fieldsets = UserAdmin.fieldsets + (
        ("Additional Info", {"fields": ("is_service_provider", "profile_picture", "bio")}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Additional Info", {"fields": ("is_service_provider", "profile_picture", "bio")}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
