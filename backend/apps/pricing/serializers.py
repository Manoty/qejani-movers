# backend/apps/pricing/serializers.py

from rest_framework import serializers
from apps.pricing.models import AddOnService, HouseSize


class QuoteRequestSerializer(serializers.Serializer):
    house_size = serializers.ChoiceField(choices=HouseSize.choices)
    distance_km = serializers.FloatField(min_value=0.1, max_value=500)
    floor_number = serializers.IntegerField(min_value=1, max_value=50, default=1)
    has_lift = serializers.BooleanField(default=False)
    addon_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        default=list,
    )

    def validate_addon_ids(self, value):
        # Convert UUIDs to strings for DB lookup
        return [str(uid) for uid in value]


class AddOnServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddOnService
        fields = ["id", "name", "description", "price"]


class HouseSizePricingSerializer(serializers.Serializer):
    """Read-only view of available house sizes and their base prices."""
    house_size = serializers.CharField()
    label = serializers.CharField(source="get_house_size_display")
    base_price = serializers.DecimalField(max_digits=10, decimal_places=2)