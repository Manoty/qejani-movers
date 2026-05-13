# backend/apps/operations/urls.py

from django.urls import path
from apps.operations import views

urlpatterns = [
    # Movers
    path("movers/", views.list_movers, name="ops-movers-list"),

    # Crew assignment
    path("bookings/<uuid:booking_id>/crew/", views.booking_crew, name="ops-booking-crew"),
    path("bookings/<uuid:booking_id>/crew/assign/", views.assign_crew, name="ops-crew-assign"),
    path("bookings/<uuid:booking_id>/crew/unassign/", views.unassign_mover, name="ops-crew-unassign"),

    # Schedule
    path("schedule/daily/", views.daily_schedule, name="ops-schedule-daily"),
    path("schedule/weekly/", views.weekly_schedule, name="ops-schedule-weekly"),
    path("schedule/movers/<uuid:mover_id>/", views.mover_schedule, name="ops-mover-schedule"),

    # Analytics
    path("analytics/overview/", views.analytics_overview, name="ops-analytics-overview"),
    path("analytics/revenue/daily/", views.analytics_daily_revenue, name="ops-analytics-revenue"),
    path("analytics/bookings/daily/", views.analytics_booking_volumes, name="ops-analytics-volumes"),
    path("analytics/house-sizes/", views.analytics_house_sizes, name="ops-analytics-house-sizes"),
]