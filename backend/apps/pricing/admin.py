# backend/apps/pricing/admin.py

from django.contrib import admin
from apps.pricing.models import AddOnService, DistanceTier, HouseSizePricing


@admin.register(HouseSizePricing)
class HouseSizePricingAdmin(admin.ModelAdmin):
    list_display = ["house_size", "base_price", "is_active", "updated_at"]
    list_editable = ["base_price", "is_active"]
    ordering = ["base_price"]


@admin.register(DistanceTier)
class DistanceTierAdmin(admin.ModelAdmin):
    list_display = ["label", "min_km", "max_km", "surcharge", "is_active"]
    list_editable = ["surcharge", "is_active"]
    ordering = ["min_km"]


@admin.register(AddOnService)
class AddOnServiceAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "is_active", "updated_at"]
    list_editable = ["price", "is_active"]
    search_fields = ["name"]
    ordering = ["name"]