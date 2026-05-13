# backend/apps/payments/views.py

import logging
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.bookings.models import Booking
from apps.bookings.permissions import IsCustomer, IsOpsOrAdmin
from apps.payments.models import Payment
from apps.payments.serializers import (
    InitiateMpesaSerializer,
    PaymentListSerializer,
    PaymentStatusSerializer,
)
from apps.payments.services import PaymentService

logger = logging.getLogger(__name__)


@api_view(["POST"])
@permission_classes([IsCustomer])
def initiate_mpesa(request, booking_id):
    """
    Customer initiates M-Pesa STK Push for their booking.
    The STK Push prompt is sent to their phone immediately.
    Poll /status/ to check the result.
    """
    booking = get_object_or_404(
        Booking,
        id=booking_id,
        customer=request.user,
    )

    serializer = InitiateMpesaSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        payment = PaymentService.initiate_mpesa(
            booking=booking,
            phone=serializer.validated_data["phone"],
            initiated_by=request.user,
        )
    except ValidationError as e:
        return Response(e.message_dict, status=status.HTTP_400_BAD_REQUEST)

    return Response(
        PaymentStatusSerializer(payment).data,
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def payment_status(request, payment_id):
    """
    Poll payment status.
    Customers can only view their own payments.
    Frontend polls this after STK Push until status is COMPLETED or FAILED.
    """
    payment = get_object_or_404(
        Payment.objects.select_related("booking__customer"),
        id=payment_id,
    )

    if request.user.is_customer and payment.booking.customer_id != request.user.id:
        return Response(
            {"detail": "You do not have permission to view this payment."},
            status=status.HTTP_403_FORBIDDEN,
        )

    return Response(PaymentStatusSerializer(payment).data)


@api_view(["POST"])
@permission_classes([IsOpsOrAdmin])
def record_cash(request, booking_id):
    """
    Ops staff records a cash payment for a booking.
    Automatically confirms the booking.
    """
    booking = get_object_or_404(Booking, id=booking_id)

    try:
        payment = PaymentService.record_cash_payment(
            booking=booking,
            initiated_by=request.user,
        )
    except ValidationError as e:
        return Response(e.message_dict, status=status.HTTP_400_BAD_REQUEST)

    return Response(
        PaymentStatusSerializer(payment).data,
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def mpesa_callback(request):
    """
    Safaricom STK Push webhook receiver.

    Security notes for production:
    - Whitelist Safaricom IP ranges at Nginx/firewall level
    - This endpoint is AllowAny because Safaricom cannot send auth headers
    - Raw payload is stored on the Payment record for audit
    - Handler is idempotent — duplicate callbacks are safely ignored
    """
    payload = request.data

    logger.info("M-Pesa callback received", extra={"payload": payload})

    payment = PaymentService.process_mpesa_callback(payload)

    # Always return 200 to Safaricom — they retry on non-200 responses
    # Even if we couldn't process it, acknowledge receipt
    return Response({"ResultCode": 0, "ResultDesc": "Accepted"})


@api_view(["GET"])
@permission_classes([IsOpsOrAdmin])
def booking_payments(request, booking_id):
    """Ops: list all payment attempts for a specific booking."""
    booking = get_object_or_404(Booking, id=booking_id)
    payments = Payment.objects.filter(booking=booking).select_related("initiated_by")
    serializer = PaymentListSerializer(payments, many=True)
    return Response(serializer.data)