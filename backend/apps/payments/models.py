# backend/apps/payments/models.py

import uuid
from django.db import models
from django.conf import settings
from apps.bookings.models import Booking


class PaymentMethod(models.TextChoices):
    MPESA = "MPESA", "M-Pesa"
    CASH  = "CASH",  "Cash"


class PaymentStatus(models.TextChoices):
    PENDING    = "PENDING",    "Pending"
    PROCESSING = "PROCESSING", "Processing"
    COMPLETED  = "COMPLETED",  "Completed"
    FAILED     = "FAILED",     "Failed"
    CANCELLED  = "CANCELLED",  "Cancelled"
    REFUNDED   = "REFUNDED",   "Refunded"


class Payment(models.Model):
    """
    One record per payment attempt.

    Key design decisions:
    - A booking can have multiple payments (retries, partial — future)
    - mpesa_checkout_request_id: Safaricom's idempotency key for webhook dedup
    - raw_callback: full Safaricom payload stored for audit/debugging
    - amount is recorded at initiation — not derived from booking,
      so we have an immutable record of what was charged
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    booking = models.ForeignKey(
        Booking,
        on_delete=models.PROTECT,
        related_name="payments",
    )
    initiated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="payments_initiated",
    )

    method = models.CharField(max_length=10, choices=PaymentMethod.choices)
    status = models.CharField(
        max_length=15,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        db_index=True,
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        help_text="Phone number charged for M-Pesa payments.",
    )

    # M-Pesa specific fields
    mpesa_checkout_request_id = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        help_text="Safaricom's CheckoutRequestID. Used for webhook deduplication.",
    )
    mpesa_merchant_request_id = models.CharField(max_length=100, blank=True)
    mpesa_receipt_number = models.CharField(
        max_length=50,
        blank=True,
        help_text="M-Pesa transaction code, e.g. QKA12BX34C. Populated on success.",
    )

    # Full raw callback payload — never parse and discard, store everything
    raw_callback = models.JSONField(
        null=True,
        blank=True,
        help_text="Full Safaricom STK Push callback payload. For audit and debugging.",
    )

    # Failure details
    failure_reason = models.TextField(blank=True)

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "payments"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["booking", "status"]),
            models.Index(fields=["mpesa_checkout_request_id"]),
        ]

    def __str__(self):
        return f"Payment {self.id} | {self.method} | {self.status} | KES {self.amount}"

    @property
    def is_successful(self):
        return self.status == PaymentStatus.COMPLETED