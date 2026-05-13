# backend/apps/operations/admin.py

from django.contrib import admin
from apps.operations.models import CrewAssignment, MoverProfile


@admin.register(MoverProfile)
class MoverProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "is_available", "updated_at"]
    list_editable = ["is_available"]
    search_fields = ["user__first_name", "user__last_name", "user__phone"]


@admin.register(CrewAssignment)
class CrewAssignmentAdmin(admin.ModelAdmin):
    list_display = ["mover", "booking", "role", "assigned_by", "created_at"]
    list_filter = ["role"]
    search_fields = ["mover__first_name", "mover__last_name", "booking__id"]
    readonly_fields = ["created_at"]