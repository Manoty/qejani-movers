# backend/apps/payments/tests/test_payments.py

import pytest
from decimal import Decimal
from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import User, Role
from apps.bookings.models import Booking, BookingStatus
from apps.bookings.services import BookingService
from apps.payments.adapters import STKPushResult
from apps.payments.models import Payment, PaymentStatus, PaymentMethod
from apps.payments.services import PaymentService
from apps.pricing.models import HouseSizePricing, DistanceTier, HouseSize


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def customer(db):
    return User.objects.create_user(
        phone="+254700000001",
        password="StrongPass123",
        first_name="Jane",
        last_name="Wanjiru",
        role=Role.CUSTOMER,
    )


@pytest.fixture
def ops_user(db):
    return User.objects.create_user(
        email="ops@qejani.co.ke",
        password="StrongPass123",
        first_name="Ops",
        last_name="Staff",
        role=Role.OPS_STAFF,
    )


@pytest.fixture(autouse=True)
def seed_pricing(db):
    HouseSizePricing.objects.create(
        house_size=HouseSize.ONE_BEDROOM,
        base_price=Decimal("15000"),
        is_active=True,
    )
    DistanceTier.objects.create(
        min_km=0, max_km=10,
        surcharge=Decimal("0"),
        label="0–10km",
        is_active=True,
    )


@pytest.fixture
def confirmed_booking(db, customer, ops_user):
    booking = BookingService.create_booking(
        customer=customer,
        house_size="ONE_BEDROOM",
        distance_km=5.0,
        pickup_address="123 Westlands Road, Nairobi",
        pickup_floor=1,
        pickup_has_lift=False,
        destination_address="456 Kilimani Avenue, Nairobi",
        addon_ids=[],
    )
    BookingService.transition_status(
        booking=booking,
        new_status=BookingStatus.CONFIRMED,
        actor=ops_user,
    )
    return booking


@pytest.fixture
def mock_stk_success():
    """Patch MpesaAdapter to return a successful STK Push result."""
    with patch("apps.payments.services.MpesaAdapter") as MockAdapter:
        instance = MockAdapter.return_value
        instance.normalize_phone.return_value = "254712345678"
        instance.initiate_stk_push.return_value = STKPushResult(
            success=True,
            checkout_request_id="ws_CO_TEST_123456789",
            merchant_request_id="MR_TEST_987654321",
        )
        yield instance


@pytest.fixture
def mock_stk_failure():
    """Patch MpesaAdapter to return a failed STK Push result."""
    with patch("apps.payments.services.MpesaAdapter") as MockAdapter:
        instance = MockAdapter.return_value
        instance.normalize_phone.return_value = "254712345678"
        instance.initiate_stk_push.return_value = STKPushResult(
            success=False,
            error="Safaricom timeout. Please try again.",
        )
        yield instance


# ── STK Push Initiation Tests ─────────────────────────────────────────────────

@pytest.mark.django_db
class TestMpesaInitiation:

    def test_successful_stk_push_creates_processing_payment(
        self, confirmed_booking, customer, mock_stk_success
    ):
        payment = PaymentService.initiate_mpesa(
            booking=confirmed_booking,
            phone="+254712345678",
            initiated_by=customer,
        )
        assert payment.status == PaymentStatus.PROCESSING
        assert payment.method == PaymentMethod.MPESA
        assert payment.mpesa_checkout_request_id == "ws_CO_TEST_123456789"
        assert payment.amount == Decimal("15000")

    def test_failed_stk_push_creates_failed_payment(
        self, confirmed_booking, customer, mock_stk_failure
    ):
        payment = PaymentService.initiate_mpesa(
            booking=confirmed_booking,
            phone="+254712345678",
            initiated_by=customer,
        )
        assert payment.status == PaymentStatus.FAILED
        assert "timeout" in payment.failure_reason.lower()

    def test_duplicate_payment_blocked(
        self, confirmed_booking, customer, mock_stk_success
    ):
        PaymentService.initiate_mpesa(
            booking=confirmed_booking,
            phone="+254712345678",
            initiated_by=customer,
        )
        from django.core.exceptions import ValidationError
        with pytest.raises(ValidationError, match="already in progress"):
            PaymentService.initiate_mpesa(
                booking=confirmed_booking,
                phone="+254712345678",
                initiated_by=customer,
            )

    def test_cancelled_booking_not_payable(self, db, customer, ops_user):
        booking = BookingService.create_booking(
            customer=customer,
            house_size="ONE_BEDROOM",
            distance_km=5.0,
            pickup_address="123 Westlands Road, Nairobi",
            pickup_floor=1,
            pickup_has_lift=False,
            destination_address="456 Kilimani Avenue, Nairobi",
            addon_ids=[],
        )
        BookingService.transition_status(
            booking=booking,
            new_status=BookingStatus.CANCELLED,
            actor=ops_user,
            cancellation_reason="Customer requested cancellation.",
        )
        from django.core.exceptions import ValidationError
        with pytest.raises(ValidationError, match="CANCELLED"):
            PaymentService.initiate_mpesa(
                booking=booking,
                phone="+254712345678",
                initiated_by=customer,
            )


# ── Webhook / Callback Tests ──────────────────────────────────────────────────

@pytest.mark.django_db
class TestMpesaCallback:

    def _make_payment(self, confirmed_booking, customer, mock_stk_success):
        return PaymentService.initiate_mpesa(
            booking=confirmed_booking,
            phone="+254712345678",
            initiated_by=customer,
        )

    def _success_payload(self, checkout_id):
        return {
            "Body": {
                "stkCallback": {
                    "CheckoutRequestID": checkout_id,
                    "ResultCode": 0,
                    "ResultDesc": "The service request is processed successfully.",
                    "CallbackMetadata": {
                        "Item": [
                            {"Name": "Amount", "Value": 15000},
                            {"Name": "MpesaReceiptNumber", "Value": "QKA12BX34C"},
                            {"Name": "TransactionDate", "Value": 20250115100000},
                            {"Name": "PhoneNumber", "Value": 254712345678},
                        ]
                    },
                }
            }
        }

    def _failure_payload(self, checkout_id):
        return {
            "Body": {
                "stkCallback": {
                    "CheckoutRequestID": checkout_id,
                    "ResultCode": 1032,
                    "ResultDesc": "Request cancelled by user.",
                }
            }
        }

    def test_successful_callback_completes_payment(
        self, confirmed_booking, customer, mock_stk_success
    ):
        payment = self._make_payment(confirmed_booking, customer, mock_stk_success)
        PaymentService.process_mpesa_callback(
            self._success_payload(payment.mpesa_checkout_request_id)
        )
        payment.refresh_from_db()
        assert payment.status == PaymentStatus.COMPLETED
        assert payment.mpesa_receipt_number == "QKA12BX34C"
        assert payment.completed_at is not None

    def test_successful_callback_confirms_booking(
        self, confirmed_booking, customer, ops_user, mock_stk_success
    ):
        # Re-open to PENDING to test auto-confirm
        confirmed_booking.status = BookingStatus.PENDING
        confirmed_booking.save()

        payment = self._make_payment(confirmed_booking, customer, mock_stk_success)
        PaymentService.process_mpesa_callback(
            self._success_payload(payment.mpesa_checkout_request_id)
        )
        confirmed_booking.refresh_from_db()
        assert confirmed_booking.status == BookingStatus.CONFIRMED

    def test_failure_callback_marks_payment_failed(
        self, confirmed_booking, customer, mock_stk_success
    ):
        payment = self._make_payment(confirmed_booking, customer, mock_stk_success)
        PaymentService.process_mpesa_callback(
            self._failure_payload(payment.mpesa_checkout_request_id)
        )
        payment.refresh_from_db()
        assert payment.status == PaymentStatus.FAILED
        assert "cancelled by user" in payment.failure_reason.lower()

    def test_duplicate_callback_is_idempotent(
        self, confirmed_booking, customer, mock_stk_success
    ):
        """Calling with the same payload twice must not change state after first."""
        payment = self._make_payment(confirmed_booking, customer, mock_stk_success)
        payload = self._success_payload(payment.mpesa_checkout_request_id)

        PaymentService.process_mpesa_callback(payload)
        payment.refresh_from_db()
        first_completed_at = payment.completed_at

        # Call again — must be a no-op
        PaymentService.process_mpesa_callback(payload)
        payment.refresh_from_db()
        assert payment.completed_at == first_completed_at
        assert payment.status == PaymentStatus.COMPLETED

    def test_unknown_checkout_id_returns_none(self):
        result = PaymentService.process_mpesa_callback(
            {
                "Body": {
                    "stkCallback": {
                        "CheckoutRequestID": "NONEXISTENT_ID",
                        "ResultCode": 0,
                        "ResultDesc": "Success",
                    }
                }
            }
        )
        assert result is None

    def test_malformed_payload_returns_none(self):
        result = PaymentService.process_mpesa_callback({"bad": "payload"})
        assert result is None


# ── Cash Payment Tests ────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestCashPayment:

    def test_ops_can_record_cash_payment(self, confirmed_booking, ops_user):
        payment = PaymentService.record_cash_payment(
            booking=confirmed_booking,
            initiated_by=ops_user,
        )
        assert payment.status == PaymentStatus.COMPLETED
        assert payment.method == PaymentMethod.CASH
        assert payment.completed_at is not None

    def test_phone_normalisation(self):
        assert MpesaAdapter.normalize_phone("+254712345678") == "254712345678"
        assert MpesaAdapter.normalize_phone("0712345678") == "254712345678"
        assert MpesaAdapter.normalize_phone("254712345678") == "254712345678"