# backend/apps/pricing/models.py

import uuid
from django.db import models
from django.core.validators import MinValueValidator


class HouseSize(models.TextChoices):
    BEDSITTER = "BEDSITTER", "Bedsitter"
    ONE_BEDROOM = "ONE_BEDROOM", "1 Bedroom"
    TWO_BEDROOM = "TWO_BEDROOM", "2 Bedroom"
    THREE_BEDROOM = "THREE_BEDROOM", "3 Bedroom"


class HouseSizePricing(models.Model):
    """
    Base price for each house size category.
    One active record per house size at any time.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    house_size = models.CharField(
        max_length=20,
        choices=HouseSize.choices,
        unique=True,
    )
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "pricing_house_sizes"
        verbose_name = "House Size Pricing"
        verbose_name_plural = "House Size Pricing"

    def __str__(self):
        return f"{self.get_house_size_display()} → KES {self.base_price:,.0f}"


class DistanceTier(models.Model):
    """
    Distance-based surcharge tiers.
    Tiers must not overlap — enforced at serializer level.

    Example:
        0–10km   → +0
        10–20km  → +3,000
        20–40km  → +7,000
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    min_km = models.PositiveIntegerField()
    max_km = models.PositiveIntegerField(null=True, blank=True, help_text="Null means no upper limit")
    surcharge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    label = models.CharField(max_length=50, help_text="e.g. '0–10km (free)'")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "pricing_distance_tiers"
        ordering = ["min_km"]
        verbose_name = "Distance Tier"
        verbose_name_plural = "Distance Tiers"

    def __str__(self):
        upper = f"{self.max_km}km" if self.max_km else "∞"
        return f"{self.min_km}km–{upper} → +KES {self.surcharge:,.0f}"


class AddOnService(models.Model):
    """
    Configurable catalog of add-on services.
    Each has a flat price. Customers select from these during booking.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "pricing_addons"
        ordering = ["name"]
        verbose_name = "Add-On Service"
        verbose_name_plural = "Add-On Services"

    def __str__(self):
        return f"{self.name} → KES {self.price:,.0f}"