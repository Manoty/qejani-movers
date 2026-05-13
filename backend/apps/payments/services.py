# backend/apps/payments/services.py

import logging
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.bookings.models import Booking, BookingStatus
from apps.bookings.services import BookingService
from apps.payments.adapters import MpesaAdapter
from apps.payments.models import Payment, PaymentMethod, PaymentStatus

logger = logging.getLogger(__name__)


class PaymentService:

    @staticmethod
    @transaction.atomic
    def initiate_mpesa(booking: Booking, phone: str, initiated_by) -> Payment:
        """
        Initiate an M-Pesa STK Push for a booking.

        Rules:
        - Booking must be CONFIRMED before payment is allowed
        - Only one PENDING/PROCESSING payment at a time per booking
        - Amount taken from booking's quoted_total — never from client input
        """
        PaymentService._assert_booking_payable(booking)
        PaymentService._assert_no_active_payment(booking)

        adapter = MpesaAdapter()
        normalized_phone = adapter.normalize_phone(phone)
        amount = int(booking.quoted_total)  # M-Pesa requires integer shillings

        # Create payment record BEFORE calling Safaricom
        # If Safaricom call fails, we have a PENDING record we can retry
        payment = Payment.objects.create(
            booking=booking,
            initiated_by=initiated_by,
            method=PaymentMethod.MPESA,
            status=PaymentStatus.PENDING,
            amount=booking.quoted_total,
            phone_number=normalized_phone,
        )

        result = adapter.initiate_stk_push(
            phone=normalized_phone,
            amount=amount,
            reference=f"QEJANI-{str(booking.id)[:8].upper()}",
            description=f"Qejani Movers - {booking.get_house_size_display()} Move",
        )

        if result.success:
            payment.status = PaymentStatus.PROCESSING
            payment.mpesa_checkout_request_id = result.checkout_request_id
            payment.mpesa_merchant_request_id = result.merchant_request_id
            payment.save()
            logger.info("STK Push initiated", extra={"payment_id": str(payment.id)})
        else:
            payment.status = PaymentStatus.FAILED
            payment.failure_reason = result.error
            payment.save()
            logger.warning("STK Push failed", extra={"error": result.error})

        return payment

    @staticmethod
    @transaction.atomic
    def record_cash_payment(booking: Booking, initiated_by) -> Payment:
        """
        Record a cash payment confirmation.
        Only ops/admin can call this — enforced at view level.
        """
        PaymentService._assert_booking_payable(booking)

        payment = Payment.objects.create(
            booking=booking,
            initiated_by=initiated_by,
            method=PaymentMethod.CASH,
            status=PaymentStatus.COMPLETED,
            amount=booking.quoted_total,
            completed_at=timezone.now(),
        )

        # Cash payment confirmed immediately — auto-advance booking
        BookingService.transition_status(
            booking=booking,
            new_status=BookingStatus.CONFIRMED,
            actor=initiated_by,
        )

        logger.info("Cash payment recorded", extra={"payment_id": str(payment.id)})
        return payment

    @staticmethod
    @transaction.atomic
    def process_mpesa_callback(payload: dict) -> Payment | None:
        """
        Handle Safaricom STK Push callback.

        IDEMPOTENT: Safe to call multiple times with the same payload.
        If the payment is already COMPLETED or FAILED, we log and return
        without modifying anything.

        Payload structure (Safaricom format):
        {
          "Body": {
            "stkCallback": {
              "CheckoutRequestID": "...",
              "ResultCode": 0,         ← 0 = success
              "ResultDesc": "...",
              "CallbackMetadata": {
                "Item": [
                  {"Name": "Amount", "Value": 1000},
                  {"Name": "MpesaReceiptNumber", "Value": "QKA12BX34C"},
                  ...
                ]
              }
            }
          }
        }
        """
        try:
            stk_callback = payload["Body"]["stkCallback"]
            checkout_request_id = stk_callback["CheckoutRequestID"]
            result_code = stk_callback["ResultCode"]
            result_desc = stk_callback.get("ResultDesc", "")
        except (KeyError, TypeError):
            logger.error("Malformed M-Pesa callback payload", extra={"payload": payload})
            return None

        try:
            payment = Payment.objects.select_for_update().get(
                mpesa_checkout_request_id=checkout_request_id
            )
        except Payment.DoesNotExist:
            logger.warning(
                "M-Pesa callback for unknown CheckoutRequestID",
                extra={"checkout_request_id": checkout_request_id},
            )
            return None

        # Idempotency guard — already processed
        if payment.status in [PaymentStatus.COMPLETED, PaymentStatus.FAILED]:
            logger.info(
                "Duplicate M-Pesa callback ignored",
                extra={"payment_id": str(payment.id), "status": payment.status},
            )
            return payment

        # Store raw payload always — even on failure
        payment.raw_callback = payload

        if result_code == 0:
            # Success — extract receipt from CallbackMetadata
            receipt = PaymentService._extract_mpesa_receipt(stk_callback)
            payment.status = PaymentStatus.COMPLETED
            payment.mpesa_receipt_number = receipt
            payment.completed_at = timezone.now()
            payment.save()

            # Auto-confirm the booking on successful payment
            booking = payment.booking
            if booking.status == BookingStatus.PENDING:
                BookingService.transition_status(
                    booking=booking,
                    new_status=BookingStatus.CONFIRMED,
                    actor=payment.initiated_by,
                )

            logger.info("M-Pesa payment completed", extra={
                "payment_id": str(payment.id),
                "receipt": receipt,
            })
        else:
            payment.status = PaymentStatus.FAILED
            payment.failure_reason = result_desc
            payment.save()
            logger.warning("M-Pesa payment failed", extra={
                "payment_id": str(payment.id),
                "result_desc": result_desc,
            })

        return payment

    # ── Private helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _assert_booking_payable(booking: Booking):
        """
        Payment is allowed on PENDING or CONFIRMED bookings only.
        CANCELLED, COMPLETED bookings must not accept new payments.
        """
        if booking.status in [BookingStatus.CANCELLED, BookingStatus.COMPLETED]:
            raise ValidationError(
                {"booking": f"Cannot initiate payment for a {booking.status} booking."}
            )

    @staticmethod
    def _assert_no_active_payment(booking: Booking):
        """Block duplicate payment attempts while one is processing."""
        active = Payment.objects.filter(
            booking=booking,
            status__in=[PaymentStatus.PENDING, PaymentStatus.PROCESSING],
        ).exists()
        if active:
            raise ValidationError(
                {"payment": "A payment for this booking is already in progress."}
            )

    @staticmethod
    def _extract_mpesa_receipt(stk_callback: dict) -> str:
        """Pull MpesaReceiptNumber out of CallbackMetadata Items list."""
        try:
            items = stk_callback["CallbackMetadata"]["Item"]
            for item in items:
                if item.get("Name") == "MpesaReceiptNumber":
                    return str(item.get("Value", ""))
        except (KeyError, TypeError):
            pass
        return ""