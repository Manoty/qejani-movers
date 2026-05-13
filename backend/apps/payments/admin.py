# backend/apps/payments/admin.py

from django.contrib import admin
from apps.payments.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        "id", "booking", "method", "status",
        "amount", "mpesa_receipt_number", "created_at",
    ]
    list_filter = ["method", "status"]
    search_fields = [
        "mpesa_receipt_number",
        "mpesa_checkout_request_id",
        "booking__id",
        "initiated_by__phone",
    ]
    readonly_fields = [
        "id", "booking", "initiated_by", "method", "amount",
        "mpesa_checkout_request_id", "mpesa_merchant_request_id",
        "mpesa_receipt_number", "raw_callback",
        "created_at", "updated_at", "completed_at",
    ]
    ordering = ["-created_at"]

    fieldsets = (
        ("Overview", {"fields": ("id", "booking", "initiated_by", "method", "status", "amount")}),
        ("M-Pesa", {"fields": (
            "phone_number",
            "mpesa_checkout_request_id",
            "mpesa_merchant_request_id",
            "mpesa_receipt_number",
            "raw_callback",
        )}),
        ("Failure", {"fields": ("failure_reason",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at", "completed_at")}),
    )