# backend/apps/payments/urls.py

from django.urls import path
from apps.payments import views

urlpatterns = [
    # Customer
    path("<uuid:booking_id>/mpesa/", views.initiate_mpesa, name="payment-mpesa-initiate"),
    path("status/<uuid:payment_id>/", views.payment_status, name="payment-status"),

    # Ops
    path("<uuid:booking_id>/cash/", views.record_cash, name="payment-cash-record"),
    path("<uuid:booking_id>/history/", views.booking_payments, name="payment-history"),

    # Safaricom webhook — no auth
    path("mpesa/callback/", views.mpesa_callback, name="mpesa-callback"),
]