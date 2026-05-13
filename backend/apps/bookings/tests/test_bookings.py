# backend/apps/bookings/tests/test_bookings.py

import pytest
from decimal import Decimal
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import User, Role
from apps.bookings.models import Booking, BookingStatus
from apps.bookings.services import BookingService
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


@pytest.fixture
def auth_customer(api_client, customer):
    api_client.force_authenticate(user=customer)
    return api_client


@pytest.fixture
def auth_ops(api_client, ops_user):
    api_client.force_authenticate(user=ops_user)
    return api_client


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
    DistanceTier.objects.create(
        min_km=10, max_km=20,
        surcharge=Decimal("3000"),
        label="10–20km",
        is_active=True,
    )


@pytest.fixture
def booking_payload():
    return {
        "house_size": "ONE_BEDROOM",
        "distance_km": 8,
        "pickup_address": "123 Westlands Road, Nairobi",
        "pickup_floor": 1,
        "pickup_has_lift": False,
        "destination_address": "456 Kilimani Avenue, Nairobi",
        "addon_ids": [],
        "inventory_notes": "Handle the TV with care.",
    }


@pytest.fixture
def existing_booking(db, customer):
    return BookingService.create_booking(
        customer=customer,
        house_size="ONE_BEDROOM",
        distance_km=8.0,
        pickup_address="123 Westlands Road, Nairobi",
        pickup_floor=1,
        pickup_has_lift=False,
        destination_address="456 Kilimani Avenue, Nairobi",
        addon_ids=[],
    )


# ── Creation Tests ────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestBookingCreation:
    def test_customer_can_create_booking(self, auth_customer, booking_payload):
        response = auth_customer.post(
            reverse("booking-create"), booking_payload, format="json"
        )
        assert response.status_code == 201
        assert response.data["status"] == BookingStatus.PENDING
        assert "quote_snapshot" in response.data
        assert Decimal(response.data["quoted_total"]) == Decimal("15000")

    def test_quote_snapshot_is_frozen(self, auth_customer, booking_payload):
        """Changing DB prices after creation must not affect existing bookings."""
        auth_customer.post(reverse("booking-create"), booking_payload, format="json")
        HouseSizePricing.objects.filter(house_size="ONE_BEDROOM").update(
            base_price=Decimal("99999")
        )
        booking = Booking.objects.first()
        assert Decimal(booking.quote_snapshot["base_price"]) == Decimal("15000")

    def test_unauthenticated_cannot_create(self, api_client, booking_payload):
        response = api_client.post(reverse("booking-create"), booking_payload, format="json")
        assert response.status_code == 401

    def test_ops_cannot_create_booking(self, auth_ops, booking_payload):
        response = auth_ops.post(reverse("booking-create"), booking_payload, format="json")
        assert response.status_code == 403

    def test_short_address_rejected(self, auth_customer, booking_payload):
        booking_payload["pickup_address"] = "too short"
        response = auth_customer.post(reverse("booking-create"), booking_payload, format="json")
        assert response.status_code == 400


# ── Status Transition Tests ───────────────────────────────────────────────────

@pytest.mark.django_db
class TestStatusTransitions:
    def test_pending_to_confirmed(self, existing_booking, ops_user):
        booking = BookingService.transition_status(
            booking=existing_booking,
            new_status=BookingStatus.CONFIRMED,
            actor=ops_user,
        )
        assert booking.status == BookingStatus.CONFIRMED
        assert booking.confirmed_at is not None

    def test_illegal_transition_raises(self, existing_booking, ops_user):
        from django.core.exceptions import ValidationError
        with pytest.raises(ValidationError):
            BookingService.transition_status(
                booking=existing_booking,
                new_status=BookingStatus.COMPLETED,  # Can't jump from PENDING to COMPLETED
                actor=ops_user,
            )

    def test_full_happy_path(self, existing_booking, ops_user):
        transitions = [
            BookingStatus.CONFIRMED,
            BookingStatus.ASSIGNED,
            BookingStatus.ON_THE_WAY,
            BookingStatus.MOVING,
            BookingStatus.COMPLETED,
        ]
        booking = existing_booking
        for new_status in transitions:
            booking = BookingService.transition_status(
                booking=booking, new_status=new_status, actor=ops_user
            )
        assert booking.status == BookingStatus.COMPLETED
        assert booking.completed_at is not None

    def test_cancel_requires_reason(self, existing_booking, ops_user):
        from django.core.exceptions import ValidationError
        with pytest.raises(ValidationError):
            BookingService.transition_status(
                booking=existing_booking,
                new_status=BookingStatus.CANCELLED,
                actor=ops_user,
                cancellation_reason="",
            )


# ── Customer Cancel Tests ─────────────────────────────────────────────────────

@pytest.mark.django_db
class TestCustomerCancellation:
    def test_customer_can_cancel_own_pending_booking(self, auth_customer, existing_booking):
        response = auth_customer.post(
            reverse("booking-cancel", kwargs={"booking_id": existing_booking.id}),
            {"cancellation_reason": "Change of plans, not moving anymore."},
            format="json",
        )
        assert response.status_code == 200
        assert response.data["status"] == BookingStatus.CANCELLED

    def test_customer_cannot_cancel_others_booking(self, db, api_client, existing_booking):
        other = User.objects.create_user(
            phone="+254700000002",
            password="StrongPass123",
            first_name="Other",
            last_name="User",
            role=Role.CUSTOMER,
        )
        api_client.force_authenticate(user=other)
        response = api_client.post(
            reverse("booking-cancel", kwargs={"booking_id": existing_booking.id}),
            {"cancellation_reason": "This is not my booking."},
            format="json",
        )
        assert response.status_code in [400, 403]

    def test_completed_booking_not_cancellable(self, existing_booking, ops_user, auth_customer):
        for s in [BookingStatus.CONFIRMED, BookingStatus.ASSIGNED,
                  BookingStatus.ON_THE_WAY, BookingStatus.MOVING, BookingStatus.COMPLETED]:
            existing_booking = BookingService.transition_status(
                booking=existing_booking, new_status=s, actor=ops_user
            )
        response = auth_customer.post(
            reverse("booking-cancel", kwargs={"booking_id": existing_booking.id}),
            {"cancellation_reason": "Too late to cancel this."},
            format="json",
        )
        assert response.status_code == 400


# ── Ops List & Filter Tests ───────────────────────────────────────────────────

@pytest.mark.django_db
class TestOpsEndpoints:
    def test_ops_can_list_all_bookings(self, auth_ops, existing_booking):
        response = auth_ops.get(reverse("ops-booking-list"))
        assert response.status_code == 200
        assert len(response.data) == 1

    def test_ops_filter_by_status(self, auth_ops, existing_booking):
        response = auth_ops.get(reverse("ops-booking-list") + "?status=PENDING")
        assert response.status_code == 200
        assert all(b["status"] == "PENDING" for b in response.data)

    def test_customer_cannot_access_ops_list(self, auth_customer):
        response = auth_customer.get(reverse("ops-booking-list"))
        assert response.status_code == 403

    def test_ops_can_update_status(self, auth_ops, existing_booking):
        response = auth_ops.patch(
            reverse("ops-booking-status", kwargs={"booking_id": existing_booking.id}),
            {"status": "CONFIRMED"},
            format="json",
        )
        assert response.status_code == 200
        assert response.data["status"] == BookingStatus.CONFIRMED