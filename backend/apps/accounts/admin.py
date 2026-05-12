# backend/apps/accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from apps.accounts.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["id", "full_name", "email", "phone", "role", "is_verified", "created_at"]
    list_filter = ["role", "is_verified", "is_active"]
    search_fields = ["email", "phone", "first_name", "last_name"]
    ordering = ["-created_at"]

    fieldsets = (
        (None, {"fields": ("email", "phone", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name")}),
        ("Role & Status", {"fields": ("role", "is_active", "is_verified", "is_staff", "is_superuser")}),
        ("Permissions", {"fields": ("groups", "user_permissions")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "phone", "password1", "password2", "role", "first_name", "last_name"),
        }),
    )