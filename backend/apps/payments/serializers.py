# backend/apps/payments/serializers.py

import re
from rest_framework import serializers
from apps.payments.models import Payment


class InitiateMpesaSerializer(serializers.Serializer):
    """Customer submits their M-Pesa phone number to receive STK Push."""
    phone = serializers.CharField(max_length=15)

    def validate_phone(self, value):
        pattern = r"^(\+2547\d{8}|07\d{8}|2547\d{8})$"
        if not re.match(pattern, value.strip()):
            raise serializers.ValidationError(
                "Enter a valid Safaricom number. Format: +2547XXXXXXXX or 07XXXXXXXX"
            )
        return value.strip()


class PaymentStatusSerializer(serializers.ModelSerializer):
    """Read-only payment status for polling."""

    class Meta:
        model = Payment
        fields = [
            "id",
            "method",
            "status",
            "amount",
            "phone_number",
            "mpesa_receipt_number",
            "failure_reason",
            "created_at",
            "completed_at",
        ]
        read_only_fields = fields


class PaymentListSerializer(serializers.ModelSerializer):
    """Ops view — list payments per booking."""
    initiated_by_name = serializers.CharField(
        source="initiated_by.full_name", read_only=True
    )

    class Meta:
        model = Payment
        fields = [
            "id",
            "method",
            "status",
            "amount",
            "phone_number",
            "mpesa_receipt_number",
            "mpesa_checkout_request_id",
            "failure_reason",
            "initiated_by_name",
            "created_at",
            "completed_at",
        ]