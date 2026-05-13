# backend/apps/bookings/services.py

import logging
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError, PermissionDenied

from apps.bookings.models import Booking, BookingStatus, ALLOWED_TRANSITIONS
from apps.pricing.data_classes import QuoteRequest
from apps.pricing.engine import PricingEngine, PricingEngineError

logger = logging.getLogger(__name__)


class BookingService:

    @staticmethod
    @transaction.atomic
    def create_booking(
        customer,
        house_size: str,
        distance_km: float,
        pickup_address: str,
        pickup_floor: int,
        pickup_has_lift: bool,
        destination_address: str,
        addon_ids: list,
        inventory_notes: str = "",
        scheduled_date=None,
        scheduled_time=None,
    ) -> Booking:
        """
        Calculate a live quote, snapshot it, and create the booking.
        The quote is calculated fresh here — never trust a quote passed in
        from the client, as it could be tampered with.
        """

        # Always recalculate server-side — never trust client-provided prices
        quote_request = QuoteRequest(
            house_size=house_size,
            distance_km=float(distance_km),
            floor_number=pickup_floor,
            has_lift=pickup_has_lift,
            addon_ids=addon_ids,
        )

        try:
            quote_result = PricingEngine.calculate(quote_request)
        except PricingEngineError as e:
            raise ValidationError({"pricing": str(e)})

        booking = Booking.objects.create(
            customer=customer,
            house_size=house_size,
            distance_km=Decimal(str(distance_km)),
            pickup_address=pickup_address,
            pickup_floor=pickup_floor,
            pickup_has_lift=pickup_has_lift,
            destination_address=destination_address,
            inventory_notes=inventory_notes,
            scheduled_date=scheduled_date,
            scheduled_time=scheduled_time,
            quote_snapshot=quote_result.to_dict(),
            quoted_total=quote_result.total,
            status=BookingStatus.PENDING,
        )

        logger.info(
            "Booking created",
            extra={
                "booking_id": str(booking.id),
                "customer_id": str(customer.id),
                "total": str(quote_result.total),
            },
        )

        return booking

    @staticmethod
    @transaction.atomic
    def transition_status(
        booking: Booking,
        new_status: str,
        actor,
        cancellation_reason: str = "",
    ) -> Booking:
        """
        Move a booking to a new status.
        Enforces the ALLOWED_TRANSITIONS rules.
        Records audit timestamps on key transitions.
        """
        allowed = ALLOWED_TRANSITIONS.get(booking.status, [])

        if new_status not in allowed:
            raise ValidationError(
                {
                    "status": (
                        f"Cannot transition from '{booking.status}' to '{new_status}'. "
                        f"Allowed transitions: {[s for s in allowed] or 'none'}."
                    )
                }
            )

        now = timezone.now()

        if new_status == BookingStatus.CONFIRMED:
            booking.confirmed_at = now
        elif new_status == BookingStatus.COMPLETED:
            booking.completed_at = now
        elif new_status == BookingStatus.CANCELLED:
            if not cancellation_reason:
                raise ValidationError({"cancellation_reason": "A reason is required when cancelling."})
            booking.cancelled_at = now
            booking.cancellation_reason = cancellation_reason

        booking.status = new_status
        booking.save()

        logger.info(
            "Booking status transitioned",
            extra={
                "booking_id": str(booking.id),
                "new_status": new_status,
                "actor_id": str(actor.id),
            },
        )

        return booking

    @staticmethod
    def cancel_by_customer(booking: Booking, customer, reason: str) -> Booking:
        """
        Customers can only cancel their own bookings,
        and only if the booking is still cancellable.
        """
        if booking.customer_id != customer.id:
            raise PermissionDenied("You do not have permission to cancel this booking.")

        if not booking.is_cancellable:
            raise ValidationError(
                {"status": f"Bookings in '{booking.status}' status cannot be cancelled."}
            )

        return BookingService.transition_status(
            booking=booking,
            new_status=BookingStatus.CANCELLED,
            actor=customer,
            cancellation_reason=reason,
        )