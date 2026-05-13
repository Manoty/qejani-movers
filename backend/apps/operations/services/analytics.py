# backend/apps/operations/services/analytics.py

from datetime import date, timedelta
from decimal import Decimal
from django.db.models import Count, Sum, Q, Avg
from django.db.models.functions import TruncDate, TruncWeek

from apps.bookings.models import Booking, BookingStatus
from apps.payments.models import Payment, PaymentStatus, PaymentMethod


class AnalyticsService:

    @staticmethod
    def get_overview(since: date, until: date) -> dict:
        """
        High-level business metrics for a date range.
        The main numbers shown on the ops dashboard header.
        """
        bookings_qs = Booking.objects.filter(
            created_at__date__gte=since,
            created_at__date__lte=until,
        )

        payments_qs = Payment.objects.filter(
            status=PaymentStatus.COMPLETED,
            completed_at__date__gte=since,
            completed_at__date__lte=until,
        )

        total_revenue = payments_qs.aggregate(
            total=Sum("amount")
        )["total"] or Decimal("0.00")

        mpesa_revenue = payments_qs.filter(method=PaymentMethod.MPESA).aggregate(
            total=Sum("amount")
        )["total"] or Decimal("0.00")

        cash_revenue = payments_qs.filter(method=PaymentMethod.CASH).aggregate(
            total=Sum("amount")
        )["total"] or Decimal("0.00")

        status_counts = (
            bookings_qs
            .values("status")
            .annotate(count=Count("id"))
        )

        return {
            "period": {"since": str(since), "until": str(until)},
            "bookings": {
                "total": bookings_qs.count(),
                "completed": bookings_qs.filter(status=BookingStatus.COMPLETED).count(),
                "cancelled": bookings_qs.filter(status=BookingStatus.CANCELLED).count(),
                "active": bookings_qs.filter(
                    status__in=[
                        BookingStatus.CONFIRMED,
                        BookingStatus.ASSIGNED,
                        BookingStatus.ON_THE_WAY,
                        BookingStatus.MOVING,
                    ]
                ).count(),
                "by_status": {item["status"]: item["count"] for item in status_counts},
            },
            "revenue": {
                "total": str(total_revenue),
                "mpesa": str(mpesa_revenue),
                "cash": str(cash_revenue),
            },
        }

    @staticmethod
    def get_daily_revenue(since: date, until: date) -> list[dict]:
        """
        Revenue broken down by day.
        Used to power the revenue chart on the dashboard.
        """
        results = (
            Payment.objects
            .filter(
                status=PaymentStatus.COMPLETED,
                completed_at__date__gte=since,
                completed_at__date__lte=until,
            )
            .annotate(day=TruncDate("completed_at"))
            .values("day")
            .annotate(
                total=Sum("amount"),
                count=Count("id"),
            )
            .order_by("day")
        )

        return [
            {
                "date": str(row["day"]),
                "revenue": str(row["total"]),
                "payment_count": row["count"],
            }
            for row in results
        ]

    @staticmethod
    def get_booking_volumes(since: date, until: date) -> list[dict]:
        """
        Booking counts by day. Separate from revenue —
        a booking is created before payment completes.
        """
        results = (
            Booking.objects
            .filter(
                created_at__date__gte=since,
                created_at__date__lte=until,
            )
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(
                total=Count("id"),
                completed=Count("id", filter=Q(status=BookingStatus.COMPLETED)),
                cancelled=Count("id", filter=Q(status=BookingStatus.CANCELLED)),
            )
            .order_by("day")
        )

        return [
            {
                "date": str(row["day"]),
                "total": row["total"],
                "completed": row["completed"],
                "cancelled": row["cancelled"],
            }
            for row in results
        ]

    @staticmethod
    def get_house_size_breakdown(since: date, until: date) -> list[dict]:
        """
        Bookings and revenue broken down by house size.
        Helps ops understand which move types drive the most volume.
        """
        results = (
            Booking.objects
            .filter(
                created_at__date__gte=since,
                created_at__date__lte=until,
                status=BookingStatus.COMPLETED,
            )
            .values("house_size")
            .annotate(
                count=Count("id"),
                total_revenue=Sum("quoted_total"),
                avg_value=Avg("quoted_total"),
            )
            .order_by("-count")
        )

        return [
            {
                "house_size": row["house_size"],
                "count": row["count"],
                "total_revenue": str(row["total_revenue"] or 0),
                "avg_value": str(row["avg_value"] or 0),
            }
            for row in results
        ]