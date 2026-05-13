# backend/apps/operations/models.py

import uuid
from django.db import models
from django.conf import settings
from apps.bookings.models import Booking


class MoverRole(models.TextChoices):
    LEAD     = "LEAD",     "Lead Mover"
    ASSISTANT= "ASSISTANT","Assistant Mover"
    DRIVER   = "DRIVER",   "Driver"


class MoverProfile(models.Model):
    """
    Extended profile for users with the MOVER role.
    Stores operational details ops staff need when assigning crew.

    One-to-one with User — created when a mover account is created.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mover_profile",
        limit_choices_to={"role": "MOVER"},
    )

    phone = models.CharField(max_length=15, blank=True)
    is_available = models.BooleanField(
        default=True,
        help_text="Manually toggled by ops when mover is on leave or unavailable.",
    )
    notes = models.TextField(blank=True, help_text="Internal ops notes about this mover.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "operations_mover_profiles"

    def __str__(self):
        return f"Mover: {self.user.full_name}"


class CrewAssignment(models.Model):
    """
    Explicit through-model for booking → mover assignment.

    Tracks:
    - Which mover was assigned
    - Their role on this job (lead, assistant, driver)
    - Who made the assignment (accountability)
    - When the assignment was made

    This is preferred over a plain ManyToMany because:
    - We need the role field per assignment
    - We need the assigned_by audit field
    - We need created_at for scheduling conflict detection
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name="crew_assignments",
    )
    mover = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="crew_assignments",
        limit_choices_to={"role": "MOVER"},
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="assignments_made",
    )

    role = models.CharField(
        max_length=15,
        choices=MoverRole.choices,
        default=MoverRole.ASSISTANT,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "operations_crew_assignments"
        # A mover can only be assigned once per booking
        unique_together = [("booking", "mover")]
        indexes = [
            models.Index(fields=["booking"]),
            models.Index(fields=["mover"]),
        ]

    def __str__(self):
        return f"{self.mover.full_name} → Booking {self.booking.id} ({self.role})"