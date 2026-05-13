# backend/apps/bookings/views.py

from django.core.exceptions import ValidationError, PermissionDenied
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.bookings.models import Booking
from apps.bookings.permissions import IsCustomer, IsOpsOrAdmin, IsBookingOwner
from apps.bookings.serializers import (
    BookingCreateSerializer,
    BookingDetailSerializer,
    BookingListSerializer,
    BookingStatusUpdateSerializer,
    CustomerCancelSerializer,
)
from apps.bookings.services import BookingService


# ── Customer Endpoints ────────────────────────────────────────────────────────

@api_view(["POST"])
@permission_classes([IsCustomer])
def create_booking(request):
    """
    Customer submits a new booking.
    Quote is recalculated server-side — client price is never trusted.
    """
    serializer = BookingCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        booking = BookingService.create_booking(
            customer=request.user,
            **serializer.validated_data,
        )
    except ValidationError as e:
        return Response(e.message_dict, status=status.HTTP_400_BAD_REQUEST)

    return Response(
        BookingDetailSerializer(booking).data,
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([IsCustomer])
def my_bookings(request):
    """List all bookings belonging to the authenticated customer."""
    bookings = (
        Booking.objects
        .filter(customer=request.user)
        .select_related("customer")
        .order_by("-created_at")
    )
    serializer = BookingListSerializer(bookings, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def booking_detail(request, booking_id):
    """
    Retrieve a single booking.
    Customers can only view their own. Ops/admin can view any.
    """
    booking = get_object_or_404(
        Booking.objects.select_related("customer"),
        id=booking_id,
    )

    if request.user.is_customer and booking.customer_id != request.user.id:
        return Response(
            {"detail": "You do not have permission to view this booking."},
            status=status.HTTP_403_FORBIDDEN,
        )

    return Response(BookingDetailSerializer(booking).data)


@api_view(["POST"])
@permission_classes([IsCustomer])
def cancel_booking(request, booking_id):
    """Customer cancels their own booking."""
    booking = get_object_or_404(Booking, id=booking_id)

    serializer = CustomerCancelSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        booking = BookingService.cancel_by_customer(
            booking=booking,
            customer=request.user,
            reason=serializer.validated_data["cancellation_reason"],
        )
    except (ValidationError, PermissionDenied) as e:
        error = e.message_dict if hasattr(e, "message_dict") else {"detail": str(e)}
        return Response(error, status=status.HTTP_400_BAD_REQUEST)

    return Response(BookingDetailSerializer(booking).data)


# ── Ops / Admin Endpoints ─────────────────────────────────────────────────────

@api_view(["GET"])
@permission_classes([IsOpsOrAdmin])
def ops_list_bookings(request):
    """
    List all bookings with optional status filter.
    Usage: /api/bookings/ops/?status=PENDING
    """
    qs = Booking.objects.select_related("customer").order_by("-created_at")

    status_filter = request.query_params.get("status")
    if status_filter:
        qs = qs.filter(status=status_filter)

    date_filter = request.query_params.get("date")
    if date_filter:
        qs = qs.filter(scheduled_date=date_filter)

    serializer = BookingListSerializer(qs, many=True)
    return Response(serializer.data)


@api_view(["PATCH"])
@permission_classes([IsOpsOrAdmin])
def ops_update_status(request, booking_id):
    """Ops staff transitions a booking to a new status."""
    booking = get_object_or_404(Booking, id=booking_id)

    serializer = BookingStatusUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        booking = BookingService.transition_status(
            booking=booking,
            new_status=serializer.validated_data["status"],
            actor=request.user,
            cancellation_reason=serializer.validated_data.get("cancellation_reason", ""),
        )
    except ValidationError as e:
        return Response(e.message_dict, status=status.HTTP_400_BAD_REQUEST)

    return Response(BookingDetailSerializer(booking).data)