# backend/apps/operations/tests/test_operations.py

import pytest
from datetime import date, timedelta
from decimal import Decimal
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import User, Role
from apps.bookings.models import Booking, BookingStatus
from apps.bookings.services import BookingService
from apps.operations.models import CrewAssignment, MoverProfile
from apps.operations.services import AssignmentService, ScheduleService, AnalyticsService
from apps.payments.models import Payment, PaymentStatus, PaymentMethod
from apps.pricing.models import DistanceTier, HouseSizePricing, HouseSize


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def customer(db):
    return User.objects.create_user(
        phone="+254700000001", password="Pass1234!",
        first_name="Jane", last_name="Wanjiru", role=Role.CUSTOMER,
    )


@pytest.fixture
def ops_user(db):
    return User.objects.create_user(
        email="ops@qejani.co.ke", password="Pass1234!",
        first_name="Ops", last_name="Staff", role=Role.OPS_STAFF,
    )


@pytest.fixture
def mover(db):
    user = User.objects.create_user(
        phone="+254700000002", password="Pass1234!",
        first_name="Brian", last_name="Omondi", role=Role.MOVER,
    )
    MoverProfile.objects.create(user=user, is_available=True)
    return user


@pytest.fixture
def mover_two(db):
    user = User.objects.create_user(
        phone="+254700000003", password="Pass1234!",
        first_name="Aisha", last_name="Kamau", role=Role.MOVER,
    )
    MoverProfile.objects.create(user=user, is_available=True)
    return user


@pytest.fixture(autouse=True)
def seed_pricing(db):
    HouseSizePricing.objects.create(
        house_size=HouseSize.ONE_BEDROOM, base_price=Decimal("15000"), is_active=True,
    )
    DistanceTier.objects.create(
        min_km=0, max_km=10, surcharge=Decimal("0"), label="0–10km", is_active=True,
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
        scheduled_date=date.today(),
    )
    BookingService.transition_status(
        booking=booking, new_status=BookingStatus.CONFIRMED, actor=ops_user
    )
    return booking


@pytest.fixture
def auth_ops(api_client, ops_user):
    api_client.force_authenticate(user=ops_user)
    return api_client


# ── Assignment Tests ──────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestCrewAssignment:

    def test_assign_single_mover(self, confirmed_booking, mover, ops_user):
        assignments = AssignmentService.assign_crew(
            booking=confirmed_booking,
            mover_ids=[str(mover.id)],
            assigned_by=ops_user,
        )
        assert len(assignments) == 1
        assert assignments[0].mover == mover

        confirmed_booking.refresh_from_db()
        assert confirmed_booking.status == BookingStatus.ASSIGNED

    def test_assign_multiple_movers(self, confirmed_booking, mover, mover_two, ops_user):
        assignments = AssignmentService.assign_crew(
            booking=confirmed_booking,
            mover_ids=[str(mover.id), str(mover_two.id)],
            assigned_by=ops_user,
        )
        assert len(assignments) == 2

    def test_assign_with_roles(self, confirmed_booking, mover, mover_two, ops_user):
        assignments = AssignmentService.assign_crew(
            booking=confirmed_booking,
            mover_ids=[str(mover.id), str(mover_two.id)],
            assigned_by=ops_user,
            roles={str(mover.id): "LEAD", str(mover_two.id): "DRIVER"},
        )
        role_map = {str(a.mover.id): a.role for a in assignments}
        assert role_map[str(mover.id)] == "LEAD"
        assert role_map[str(mover_two.id)] == "DRIVER"

    def test_scheduling_conflict_detected(self, db, confirmed_booking, mover, ops_user, customer):
        # Assign mover to first booking
        AssignmentService.assign_crew(
            booking=confirmed_booking,
            mover_ids=[str(mover.id)],
            assigned_by=ops_user,
        )

        # Create second booking same day
        second = BookingService.create_booking(
            customer=customer,
            house_size="ONE_BEDROOM",
            distance_km=5.0,
            pickup_address="789 Karen Road, Nairobi",
            pickup_floor=1,
            pickup_has_lift=False,
            destination_address="321 Ngong Avenue, Nairobi",
            addon_ids=[],
            scheduled_date=date.today(),
        )
        BookingService.transition_status(
            booking=second, new_status=BookingStatus.CONFIRMED, actor=ops_user
        )

        from django.core.exceptions import ValidationError
        with pytest.raises(ValidationError, match="already assigned"):
            AssignmentService.assign_crew(
                booking=second,
                mover_ids=[str(mover.id)],
                assigned_by=ops_user,
            )

    def test_unavailable_mover_rejected(self, confirmed_booking, mover, ops_user):
        mover.mover_profile.is_available = False
        mover.mover_profile.save()

        from django.core.exceptions import ValidationError
        with pytest.raises(ValidationError, match="unavailable"):
            AssignmentService.assign_crew(
                booking=confirmed_booking,
                mover_ids=[str(mover.id)],
                assigned_by=ops_user,
            )

    def test_unassign_mover(self, confirmed_booking, mover, ops_user):
        AssignmentService.assign_crew(
            booking=confirmed_booking,
            mover_ids=[str(mover.id)],
            assigned_by=ops_user,
        )
        AssignmentService.unassign_mover(
            booking=confirmed_booking,
            mover_id=str(mover.id),
            removed_by=ops_user,
        )
        assert not CrewAssignment.objects.filter(
            booking=confirmed_booking, mover=mover
        ).exists()

    def test_pending_booking_not_assignable(self, db, customer, mover, ops_user):
        pending = BookingService.create_booking(
            customer=customer,
            house_size="ONE_BEDROOM",
            distance_km=5.0,
            pickup_address="123 Westlands Road, Nairobi",
            pickup_floor=1,
            pickup_has_lift=False,
            destination_address="456 Kilimani Avenue, Nairobi",
            addon_ids=[],
        )
        from django.core.exceptions import ValidationError
        with pytest.raises(ValidationError, match="CONFIRMED"):
            AssignmentService.assign_crew(
                booking=pending,
                mover_ids=[str(mover.id)],
                assigned_by=ops_user,
            )


# ── Schedule Tests ────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestScheduleService:

    def test_daily_schedule_returns_booking(self, confirmed_booking):
        result = ScheduleService.get_daily_schedule(date.today())
        assert result["total_bookings"] == 1
        assert confirmed_booking in list(result["bookings"])

    def test_daily_schedule_empty_for_other_date(self, confirmed_booking):
        result = ScheduleService.get_daily_schedule(date.today() + timedelta(days=5))
        assert result["total_bookings"] == 0

    def test_weekly_schedule_returns_7_days(self, confirmed_booking):
        result = ScheduleService.get_weekly_schedule(date.today())
        assert len(result) == 7


# ── Analytics Tests ───────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestAnalyticsService:

    def test_overview_counts_bookings(self, confirmed_booking):
        result = AnalyticsService.get_overview(
            since=date.today() - timedelta(days=1),
            until=date.today(),
        )
        assert result["bookings"]["total"] >= 1

    def test_overview_revenue_zero_without_payments(self, confirmed_booking):
        result = AnalyticsService.get_overview(
            since=date.today() - timedelta(days=1),
            until=date.today(),
        )
        assert result["revenue"]["total"] == "0.00"

    def test_overview_counts_revenue_from_completed_payments(
        self, confirmed_booking, ops_user
    ):
        Payment.objects.create(
            booking=confirmed_booking,
            initiated_by=ops_user,
            method=PaymentMethod.CASH,
            status=PaymentStatus.COMPLETED,
            amount=Decimal("15000"),
            completed_at=confirmed_booking.created_at,
        )
        result = AnalyticsService.get_overview(
            since=date.today() - timedelta(days=1),
            until=date.today(),
        )
        assert Decimal(result["revenue"]["total"]) == Decimal("15000")

    def test_house_size_breakdown_empty_without_completed(self):
        result = AnalyticsService.get_house_size_breakdown(
            since=date.today() - timedelta(days=1),
            until=date.today(),
        )
        assert result == []


# ── API Endpoint Tests ────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestOpsAPIEndpoints:

    def test_list_movers(self, auth_ops, mover):
        response = auth_ops.get(reverse("ops-movers-list"))
        assert response.status_code == 200
        assert len(response.data) == 1

    def test_assign_crew_via_api(self, auth_ops, confirmed_booking, mover):
        response = auth_ops.post(
            reverse("ops-crew-assign", kwargs={"booking_id": confirmed_booking.id}),
            {"mover_ids": [str(mover.id)]},
            format="json",
        )
        assert response.status_code == 201
        assert len(response.data) == 1

    def test_daily_schedule_via_api(self, auth_ops, confirmed_booking):
        response = auth_ops.get(
            reverse("ops-schedule-daily") + f"?date={date.today()}"
        )
        assert response.status_code == 200
        assert response.data["total_bookings"] == 1

    def test_analytics_overview_via_api(self, auth_ops):
        response = auth_ops.get(reverse("ops-analytics-overview"))
        assert response.status_code == 200
        assert "bookings" in response.data
        assert "revenue" in response.data

    def test_customer_cannot_access_ops_endpoints(self, api_client, customer):
        api_client.force_authenticate(user=customer)
        response = api_client.get(reverse("ops-movers-list"))
        assert response.status_code == 403