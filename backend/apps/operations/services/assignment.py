# backend/apps/operations/services/assignment.py

import logging
from django.db import transaction
from django.core.exceptions import ValidationError

from apps.accounts.models import User, Role
from apps.bookings.models import Booking, BookingStatus
from apps.bookings.services import BookingService
from apps.operations.models import CrewAssignment, MoverRole

logger = logging.getLogger(__name__)


class AssignmentService:

    @staticmethod
    @transaction.atomic
    def assign_crew(
        booking: Booking,
        mover_ids: list[str],
        assigned_by: User,
        roles: dict[str, str] | None = None,
    ) -> list[CrewAssignment]:
        """
        Assign one or more movers to a booking.

        Args:
            booking:     The booking to assign crew to.
            mover_ids:   List of User UUIDs (must have MOVER role).
            assigned_by: The ops/admin user making the assignment.
            roles:       Optional dict of {mover_id: MoverRole}.
                         Defaults to ASSISTANT if not specified.

        Rules:
        - Booking must be CONFIRMED before crew can be assigned.
        - Each mover must have MOVER role and be available.
        - Scheduling conflict check: mover cannot be on two jobs
          on the same scheduled_date.
        - After successful assignment, booking transitions to ASSIGNED.
        """
        roles = roles or {}

        AssignmentService._assert_booking_assignable(booking)

        movers = AssignmentService._fetch_and_validate_movers(mover_ids)

        assignments = []
        for mover in movers:
            AssignmentService._check_scheduling_conflict(mover, booking)

            role = roles.get(str(mover.id), MoverRole.ASSISTANT)

            assignment, created = CrewAssignment.objects.get_or_create(
                booking=booking,
                mover=mover,
                defaults={
                    "assigned_by": assigned_by,
                    "role": role,
                },
            )

            if not created:
                # Update role if already assigned
                assignment.role = role
                assignment.assigned_by = assigned_by
                assignment.save()

            assignments.append(assignment)

        # Transition booking to ASSIGNED
        if booking.status == BookingStatus.CONFIRMED:
            BookingService.transition_status(
                booking=booking,
                new_status=BookingStatus.ASSIGNED,
                actor=assigned_by,
            )

        logger.info(
            "Crew assigned to booking",
            extra={
                "booking_id": str(booking.id),
                "mover_ids": mover_ids,
                "assigned_by": str(assigned_by.id),
            },
        )

        return assignments

    @staticmethod
    @transaction.atomic
    def unassign_mover(booking: Booking, mover_id: str, removed_by: User) -> None:
        """Remove a single mover from a booking."""
        try:
            assignment = CrewAssignment.objects.get(
                booking=booking,
                mover_id=mover_id,
            )
        except CrewAssignment.DoesNotExist:
            raise ValidationError(
                {"mover": "This mover is not assigned to the booking."}
            )

        assignment.delete()

        logger.info(
            "Mover unassigned from booking",
            extra={
                "booking_id": str(booking.id),
                "mover_id": mover_id,
                "removed_by": str(removed_by.id),
            },
        )

    # ── Private helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _assert_booking_assignable(booking: Booking):
        if booking.status not in [BookingStatus.CONFIRMED, BookingStatus.ASSIGNED]:
            raise ValidationError(
                {
                    "booking": (
                        f"Cannot assign crew to a booking with status '{booking.status}'. "
                        "Booking must be CONFIRMED or ASSIGNED."
                    )
                }
            )

    @staticmethod
    def _fetch_and_validate_movers(mover_ids: list[str]) -> list[User]:
        if not mover_ids:
            raise ValidationError({"movers": "At least one mover must be assigned."})

        movers = list(
            User.objects.filter(id__in=mover_ids, role=Role.MOVER, is_active=True)
        )

        if len(movers) != len(mover_ids):
            found_ids = {str(m.id) for m in movers}
            missing = [mid for mid in mover_ids if mid not in found_ids]
            raise ValidationError(
                {"movers": f"Invalid or inactive mover IDs: {missing}"}
            )

        unavailable = [m for m in movers if not m.mover_profile.is_available]
        if unavailable:
            names = [m.full_name for m in unavailable]
            raise ValidationError(
                {"movers": f"These movers are marked unavailable: {names}"}
            )

        return movers

    @staticmethod
    def _check_scheduling_conflict(mover: User, booking: Booking):
        """
        A mover cannot be on two different bookings on the same day.
        Skips check if booking has no scheduled_date (can always assign).
        """
        if not booking.scheduled_date:
            return

        conflict = CrewAssignment.objects.filter(
            mover=mover,
            booking__scheduled_date=booking.scheduled_date,
            booking__status__in=[
                BookingStatus.CONFIRMED,
                BookingStatus.ASSIGNED,
                BookingStatus.ON_THE_WAY,
                BookingStatus.MOVING,
            ],
        ).exclude(booking=booking).exists()

        if conflict:
            raise ValidationError(
                {
                    "movers": (
                        f"{mover.full_name} is already assigned to another booking "
                        f"on {booking.scheduled_date}."
                    )
                }
            )