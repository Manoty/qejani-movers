# backend/apps/bookings/models.py

import uuid
from django.db import models
from django.conf import settings
from apps.pricing.models import HouseSize


class BookingStatus(models.TextChoices):
    PENDING    = "PENDING",    "Pending"
    CONFIRMED  = "CONFIRMED",  "Confirmed"
    ASSIGNED   = "ASSIGNED",   "Assigned"
    ON_THE_WAY = "ON_THE_WAY", "On The Way"
    MOVING     = "MOVING",     "Moving"
    COMPLETED  = "COMPLETED",  "Completed"
    CANCELLED  = "CANCELLED",  "Cancelled"


# Legal status transitions. Only these moves are allowed.
# Enforced in the service layer — not at model level, so we can test it.
ALLOWED_TRANSITIONS = {
    BookingStatus.PENDING:    [BookingStatus.CONFIRMED, BookingStatus.CANCELLED],
    BookingStatus.CONFIRMED:  [BookingStatus.ASSIGNED,  BookingStatus.CANCELLED],
    BookingStatus.ASSIGNED:   [BookingStatus.ON_THE_WAY],
    BookingStatus.ON_THE_WAY: [BookingStatus.MOVING],
    BookingStatus.MOVING:     [BookingStatus.COMPLETED],
    BookingStatus.COMPLETED:  [],
    BookingStatus.CANCELLED:  [],
}


class Booking(models.Model):
    """
    A customer's moving booking.

    Key design decisions:
    - quote_snapshot: frozen JSON of the QuoteResult at time of booking.
      Price changes never retroactively affect confirmed bookings.
    - pickup/destination as structured fields (not a single string) so
      we can later add map integration, distance validation, routing.
    - scheduled_date is nullable — customer can book first, schedule later.
    - status transitions enforced in service layer via ALLOWED_TRANSITIONS.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Ownership
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="bookings",
        limit_choices_to={"role": "CUSTOMER"},
    )

    # Status lifecycle
    status = models.CharField(
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING,
        db_index=True,
    )

    # Move details
    house_size = models.CharField(max_length=20, choices=HouseSize.choices)
    scheduled_date = models.DateField(null=True, blank=True)
    scheduled_time = models.TimeField(null=True, blank=True)

    # Locations — structured for future map integration
    pickup_address = models.TextField()
    pickup_floor = models.PositiveIntegerField(default=1)
    pickup_has_lift = models.BooleanField(default=False)

    destination_address = models.TextField()

    # Distance recorded at time of booking (used in quote)
    distance_km = models.DecimalField(max_digits=6, decimal_places=2)

    # Frozen quote — never recalculated after this is set
    quote_snapshot = models.JSONField(
        help_text="Frozen copy of QuoteResult at time of booking. Never modified after creation."
    )

    # Quoted total pulled out for easy querying/display
    quoted_total = models.DecimalField(max_digits=10, decimal_places=2)

    # Customer notes about items to move
    inventory_notes = models.TextField(blank=True)

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)

    class Meta:
        db_table = "bookings"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["customer", "status"]),
            models.Index(fields=["status", "scheduled_date"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"Booking {self.id} | {self.customer} | {self.status}"

    @property
    def is_cancellable(self):
        return self.status in [BookingStatus.PENDING, BookingStatus.CONFIRMED]

    @property
    def can_transition_to(self):
        return ALLOWED_TRANSITIONS.get(self.status, [])