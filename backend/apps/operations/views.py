# backend/apps/operations/views.py

from datetime import date
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from apps.accounts.models import User, Role
from apps.bookings.models import Booking
from apps.bookings.permissions import IsOpsOrAdmin
from apps.operations.models import MoverProfile, CrewAssignment
from apps.operations.serializers import (
    AnalyticsQuerySerializer,
    AssignCrewSerializer,
    CrewAssignmentSerializer,
    DailyScheduleSerializer,
    MoverProfileSerializer,
    ScheduledBookingSerializer,
    UnassignMoverSerializer,
)
from apps.operations.services import AssignmentService, ScheduleService, AnalyticsService


# ── Crew Management ───────────────────────────────────────────────────────────

@api_view(["GET"])
@permission_classes([IsOpsOrAdmin])
def list_movers(request):
    """
    All active mover profiles.
    Used by ops to select crew when assigning bookings.
    """
    movers = (
        MoverProfile.objects
        .filter(user__is_active=True)
        .select_related("user")
        .order_by("user__first_name")
    )
    serializer = MoverProfileSerializer(movers, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsOpsOrAdmin])
def assign_crew(request, booking_id):
    """Assign one or more movers to a booking."""
    booking = get_object_or_404(Booking, id=booking_id)

    serializer = AssignCrewSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        assignments = AssignmentService.assign_crew(
            booking=booking,
            mover_ids=serializer.validated_data["mover_ids"],
            assigned_by=request.user,
            roles=serializer.validated_data.get("roles", {}),
        )
    except ValidationError as e:
        return Response(e.message_dict, status=status.HTTP_400_BAD_REQUEST)

    return Response(
        CrewAssignmentSerializer(assignments, many=True).data,
        status=status.HTTP_201_CREATED,
    )


@api_view(["DELETE"])
@permission_classes([IsOpsOrAdmin])
def unassign_mover(request, booking_id):
    """Remove a specific mover from a booking."""
    booking = get_object_or_404(Booking, id=booking_id)

    serializer = UnassignMoverSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        AssignmentService.unassign_mover(
            booking=booking,
            mover_id=serializer.validated_data["mover_id"],
            removed_by=request.user,
        )
    except ValidationError as e:
        return Response(e.message_dict, status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
@permission_classes([IsOpsOrAdmin])
def booking_crew(request, booking_id):
    """List all crew assigned to a booking."""
    booking = get_object_or_404(Booking, id=booking_id)
    assignments = (
        CrewAssignment.objects
        .filter(booking=booking)
        .select_related("mover", "assigned_by")
    )
    return Response(CrewAssignmentSerializer(assignments, many=True).data)


# ── Schedule Views ────────────────────────────────────────────────────────────

@api_view(["GET"])
@permission_classes([IsOpsOrAdmin])
def daily_schedule(request):
    """
    Full schedule for a given date.
    Query param: ?date=2025-01-15 (defaults to today)
    """
    date_str = request.query_params.get("date")
    try:
        target_date = date.fromisoformat(date_str) if date_str else date.today()
    except ValueError:
        return Response(
            {"detail": "Invalid date format. Use YYYY-MM-DD."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    schedule = ScheduleService.get_daily_schedule(target_date)

    return Response({
        "date": schedule["date"],
        "total_bookings": schedule["total_bookings"],
        "bookings": ScheduledBookingSerializer(schedule["bookings"], many=True).data,
    })


@api_view(["GET"])
@permission_classes([IsOpsOrAdmin])
def weekly_schedule(request):
    """
    7-day schedule starting from ?start_date (defaults to today).
    """
    date_str = request.query_params.get("start_date")
    try:
        start_date = date.fromisoformat(date_str) if date_str else date.today()
    except ValueError:
        return Response(
            {"detail": "Invalid date format. Use YYYY-MM-DD."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    weekly = ScheduleService.get_weekly_schedule(start_date)

    return Response([
        {
            "date": day["date"],
            "total_bookings": day["total_bookings"],
            "bookings": ScheduledBookingSerializer(day["bookings"], many=True).data,
        }
        for day in weekly
    ])


@api_view(["GET"])
@permission_classes([IsOpsOrAdmin])
def mover_schedule(request, mover_id):
    """Schedule for a specific mover on a given date."""
    date_str = request.query_params.get("date")
    try:
        target_date = date.fromisoformat(date_str) if date_str else date.today()
    except ValueError:
        return Response(
            {"detail": "Invalid date format. Use YYYY-MM-DD."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    schedule = ScheduleService.get_mover_schedule(str(mover_id), target_date)

    return Response({
        "date": schedule["date"],
        "mover_id": schedule["mover_id"],
        "assignments": CrewAssignmentSerializer(schedule["assignments"], many=True).data,
    })


# ── Analytics ─────────────────────────────────────────────────────────────────

@api_view(["GET"])
@permission_classes([IsOpsOrAdmin])
def analytics_overview(request):
    """
    High-level business metrics.
    Query params: ?since=2025-01-01&until=2025-01-31
    Defaults to last 30 days.
    """
    serializer = AnalyticsQuerySerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)
    data = AnalyticsService.get_overview(**serializer.validated_data)
    return Response(data)


@api_view(["GET"])
@permission_classes([IsOpsOrAdmin])
def analytics_daily_revenue(request):
    """Daily revenue breakdown for charting."""
    serializer = AnalyticsQuerySerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)
    data = AnalyticsService.get_daily_revenue(**serializer.validated_data)
    return Response(data)


@api_view(["GET"])
@permission_classes([IsOpsOrAdmin])
def analytics_booking_volumes(request):
    """Daily booking volume breakdown."""
    serializer = AnalyticsQuerySerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)
    data = AnalyticsService.get_booking_volumes(**serializer.validated_data)
    return Response(data)


@api_view(["GET"])
@permission_classes([IsOpsOrAdmin])
def analytics_house_sizes(request):
    """Revenue and volume breakdown by house size."""
    serializer = AnalyticsQuerySerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)
    data = AnalyticsService.get_house_size_breakdown(**serializer.validated_data)
    return Response(data)