# backend/apps/accounts/services.py

from django.db import transaction
from django.core.exceptions import ValidationError
from apps.accounts.models import User, Role


class CustomerRegistrationService:
    """
    Handles all logic for registering a new customer.
    Isolated here so it can be called from API views,
    admin tools, or management commands without duplication.
    """

    @staticmethod
    @transaction.atomic
    def register(
        phone: str,
        password: str,
        first_name: str,
        last_name: str,
    ) -> User:
        if User.objects.filter(phone=phone).exists():
            raise ValidationError({"phone": "A user with this phone number already exists."})

        user = User.objects.create_user(
            phone=phone,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=Role.CUSTOMER,
            is_verified=False,
        )
        return user


class StaffRegistrationService:
    """
    Handles registration of internal staff accounts.
    Only callable by admins (enforced at view level).
    """

    @staticmethod
    @transaction.atomic
    def register(
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        role: str,
    ) -> User:
        allowed_roles = [Role.ADMIN, Role.OPS_STAFF, Role.MOVER]
        if role not in allowed_roles:
            raise ValidationError({"role": f"Invalid staff role: {role}"})

        if User.objects.filter(email=email).exists():
            raise ValidationError({"email": "A user with this email already exists."})

        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role,
            is_staff=(role == Role.ADMIN),
            is_verified=True,
        )
        return user