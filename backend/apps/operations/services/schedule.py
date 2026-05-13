# backend/apps/operations/services/schedule.py

from datetime import date, timedelta
from django.db.models import Prefetch
from apps.bookings.models import Booking, BookingStatus
from apps.operations.models import CrewAssignment


ACTIVE_STATUSES = [
    BookingStatus.CONFIRMED,
    BookingStatus.ASSIGNED,
    BookingStatus.ON_THE_WAY,
    BookingStatus.MOVING,
]


class ScheduleService:

    @staticmethod
    def get_daily_schedule(target_date: date) -> dict:
        """
        All active bookings for a given date with their crew.
        Used by ops to see the full day's workload.
        """
        bookings = (
            Booking.objects
            .filter(scheduled_date=target_date, status__in=ACTIVE_STATUSES)
            .select_related("customer")
            .prefetch_related(
                Prefetch(
                    "crew_assignments",
                    queryset=CrewAssignment.objects.select_related("mover"),
                )
            )
            .order_by("scheduled_time")
        )

        return {
            "date": str(target_date),
            "total_bookings": bookings.count(),
            "bookings": bookings,
        }

    @staticmethod
    def get_weekly_schedule(start_date: date) -> list[dict]:
        """
        Day-by-day schedule for the 7 days starting from start_date.
        """
        return [
            ScheduleService.get_daily_schedule(start_date + timedelta(days=i))
            for i in range(7)
        ]

    @staticmethod
    def get_mover_schedule(mover_id: str, target_date: date) -> dict:
        """
        All bookings a specific mover is assigned to on a given date.
        Used by movers to see their own assignments.
        """
        assignments = (
            CrewAssignment.objects
            .filter(
                mover_id=mover_id,
                booking__scheduled_date=target_date,
                booking__status__in=ACTIVE_STATUSES,
            )
            .select_related("booking__customer", "mover")
            .order_by("booking__scheduled_time")
        )

        return {
            "date": str(target_date),
            "mover_id": mover_id,
            "assignments": assignments,
        }