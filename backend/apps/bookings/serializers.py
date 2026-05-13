# backend/apps/bookings/serializers.py

from rest_framework import serializers
from apps.bookings.models import Booking, BookingStatus, ALLOWED_TRANSITIONS
from apps.pricing.models import HouseSize


class BookingCreateSerializer(serializers.Serializer):
    """Input for creating a new booking."""
    house_size = serializers.ChoiceField(choices=HouseSize.choices)
    distance_km = serializers.FloatField(min_value=0.1, max_value=500)
    pickup_address = serializers.CharField(max_length=500)
    pickup_floor = serializers.IntegerField(min_value=1, max_value=50, default=1)
    pickup_has_lift = serializers.BooleanField(default=False)
    destination_address = serializers.CharField(max_length=500)
    addon_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        default=list,
    )
    inventory_notes = serializers.CharField(required=False, allow_blank=True, default="")
    scheduled_date = serializers.DateField(required=False, allow_null=True)
    scheduled_time = serializers.TimeField(required=False, allow_null=True)

    def validate_addon_ids(self, value):
        return [str(uid) for uid in value]

    def validate_pickup_address(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Please provide a complete pickup address.")
        return value.strip()

    def validate_destination_address(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Please provide a complete destination address.")
        return value.strip()


class BookingListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views — no nested snapshot."""
    customer_name = serializers.CharField(source="customer.full_name", read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "customer_name",
            "house_size",
            "status",
            "quoted_total",
            "scheduled_date",
            "pickup_address",
            "destination_address",
            "created_at",
        ]


class BookingDetailSerializer(serializers.ModelSerializer):
    """Full detail serializer — includes quote snapshot and all fields."""
    customer_name = serializers.CharField(source="customer.full_name", read_only=True)
    customer_phone = serializers.CharField(source="customer.phone", read_only=True)
    can_transition_to = serializers.SerializerMethodField()
    is_cancellable = serializers.BooleanField(read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "customer_name",
            "customer_phone",
            "house_size",
            "status",
            "scheduled_date",
            "scheduled_time",
            "pickup_address",
            "pickup_floor",
            "pickup_has_lift",
            "destination_address",
            "distance_km",
            "quote_snapshot",
            "quoted_total",
            "inventory_notes",
            "is_cancellable",
            "can_transition_to",
            "created_at",
            "confirmed_at",
            "completed_at",
            "cancelled_at",
            "cancellation_reason",
        ]

    def get_can_transition_to(self, obj):
        return list(ALLOWED_TRANSITIONS.get(obj.status, []))


class BookingStatusUpdateSerializer(serializers.Serializer):
    """Used by ops staff to transition a booking status."""
    status = serializers.ChoiceField(choices=BookingStatus.choices)
    cancellation_reason = serializers.CharField(required=False, allow_blank=True, default="")

    def validate(self, data):
        if data["status"] == BookingStatus.CANCELLED and not data.get("cancellation_reason"):
            raise serializers.ValidationError(
                {"cancellation_reason": "Required when cancelling a booking."}
            )
        return data


class CustomerCancelSerializer(serializers.Serializer):
    """Used by customers to cancel their own booking."""
    cancellation_reason = serializers.CharField(min_length=10)