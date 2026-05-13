# backend/apps/operations/serializers.py

from rest_framework import serializers
from apps.operations.models import CrewAssignment, MoverProfile, MoverRole
from apps.bookings.serializers import BookingListSerializer
from apps.accounts.models import User, Role


class MoverProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    phone = serializers.CharField(source="user.phone", read_only=True)
    user_id = serializers.UUIDField(source="user.id", read_only=True)

    class Meta:
        model = MoverProfile
        fields = ["user_id", "full_name", "phone", "is_available", "notes"]


class CrewAssignmentSerializer(serializers.ModelSerializer):
    mover_name = serializers.CharField(source="mover.full_name", read_only=True)
    mover_phone = serializers.CharField(source="mover.phone", read_only=True)
    assigned_by_name = serializers.CharField(source="assigned_by.full_name", read_only=True)

    class Meta:
        model = CrewAssignment
        fields = ["id", "mover", "mover_name", "mover_phone", "role", "assigned_by_name", "created_at"]
        read_only_fields = ["id", "assigned_by_name", "created_at"]


class AssignCrewSerializer(serializers.Serializer):
    """Input for assigning crew to a booking."""
    mover_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        max_length=10,
    )
    roles = serializers.DictField(
        child=serializers.ChoiceField(choices=MoverRole.choices),
        required=False,
        default=dict,
        help_text="Optional map of {mover_id: role}. Defaults to ASSISTANT.",
    )

    def validate_mover_ids(self, value):
        return [str(uid) for uid in value]

    def validate_roles(self, value):
        return {str(k): v for k, v in value.items()}


class UnassignMoverSerializer(serializers.Serializer):
    mover_id = serializers.UUIDField()

    def validate_mover_id(self, value):
        return str(value)


class ScheduledBookingSerializer(serializers.ModelSerializer):
    """Booking with crew for schedule views."""
    customer_name = serializers.CharField(source="customer.full_name", read_only=True)
    customer_phone = serializers.CharField(source="customer.phone", read_only=True)
    crew = CrewAssignmentSerializer(source="crew_assignments", many=True, read_only=True)

    class Meta:
        from apps.bookings.models import Booking
        model = Booking
        fields = [
            "id", "status", "house_size",
            "scheduled_date", "scheduled_time",
            "pickup_address", "destination_address",
            "quoted_total", "customer_name", "customer_phone",
            "crew",
        ]


class DailyScheduleSerializer(serializers.Serializer):
    date = serializers.DateField()
    total_bookings = serializers.IntegerField()
    bookings = ScheduledBookingSerializer(many=True)


class AnalyticsQuerySerializer(serializers.Serializer):
    """Query params for analytics endpoints."""
    since = serializers.DateField(required=False)
    until = serializers.DateField(required=False)

    def validate(self, data):
        from datetime import date, timedelta
        today = date.today()
        data.setdefault("since", today - timedelta(days=30))
        data.setdefault("until", today)
        if data["since"] > data["until"]:
            raise serializers.ValidationError(
                {"since": "'since' must be before 'until'."}
            )
        return data