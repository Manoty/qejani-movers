# backend/apps/bookings/urls.py

from django.urls import path
from apps.bookings import views

urlpatterns = [
    # Customer
    path("", views.create_booking, name="booking-create"),
    path("mine/", views.my_bookings, name="booking-list-mine"),
    path("<uuid:booking_id>/", views.booking_detail, name="booking-detail"),
    path("<uuid:booking_id>/cancel/", views.cancel_booking, name="booking-cancel"),

    # Ops / Admin
    path("ops/", views.ops_list_bookings, name="ops-booking-list"),
    path("ops/<uuid:booking_id>/status/", views.ops_update_status, name="ops-booking-status"),
]