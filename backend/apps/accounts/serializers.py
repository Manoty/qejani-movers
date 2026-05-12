# backend/apps/accounts/serializers.py

from rest_framework import serializers
from apps.accounts.models import User, Role


class CustomerRegisterSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    password = serializers.CharField(min_length=8, write_only=True)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)

    def validate_phone(self, value):
        # Enforce Kenyan phone format: +2547XXXXXXXX or 07XXXXXXXX
        import re
        pattern = r"^(\+2547\d{8}|07\d{8})$"
        if not re.match(pattern, value):
            raise serializers.ValidationError(
                "Enter a valid Kenyan phone number. Format: +2547XXXXXXXX or 07XXXXXXXX"
            )
        return value


class StaffRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    role = serializers.ChoiceField(choices=[Role.ADMIN, Role.OPS_STAFF, Role.MOVER])


class CustomerLoginSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    password = serializers.CharField(write_only=True)


class StaffLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "phone",
            "first_name",
            "last_name",
            "full_name",
            "role",
            "is_verified",
            "created_at",
        ]
        read_only_fields = ["id", "role", "is_verified", "created_at"]