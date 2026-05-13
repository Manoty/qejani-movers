# backend/apps/bookings/admin.py

from django.contrib import admin
from apps.bookings.models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        "id", "customer", "house_size", "status",
        "quoted_total", "scheduled_date", "created_at",
    ]
    list_filter = ["status", "house_size", "scheduled_date"]
    search_fields = ["customer__phone", "customer__email", "pickup_address", "destination_address"]
    readonly_fields = [
        "id", "quote_snapshot", "quoted_total", "created_at",
        "confirmed_at", "completed_at", "cancelled_at",
    ]
    ordering = ["-created_at"]

    fieldsets = (
        ("Overview", {"fields": ("id", "customer", "status", "house_size")}),
        ("Locations", {"fields": ("pickup_address", "pickup_floor", "pickup_has_lift", "destination_address", "distance_km")}),
        ("Schedule", {"fields": ("scheduled_date", "scheduled_time")}),
        ("Pricing", {"fields": ("quote_snapshot", "quoted_total")}),
        ("Notes", {"fields": ("inventory_notes", "cancellation_reason")}),
        ("Timestamps", {"fields": ("created_at", "confirmed_at", "completed_at", "cancelled_at")}),
    )