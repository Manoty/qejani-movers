# backend/apps/accounts/models.py

import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class Role(models.TextChoices):
    CUSTOMER = "CUSTOMER", "Customer"
    ADMIN = "ADMIN", "Admin"
    OPS_STAFF = "OPS_STAFF", "Operations Staff"
    MOVER = "MOVER", "Mover"


class UserManager(BaseUserManager):
    """
    Custom manager supporting both phone-based (customers)
    and email-based (staff) creation paths.
    """

    def create_user(self, email=None, phone=None, password=None, **extra_fields):
        if not email and not phone:
            raise ValueError("User must have either an email or phone number.")

        if email:
            email = self.normalize_email(email)

        user = self.model(email=email, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("role", Role.ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_verified", True)
        return self.create_user(email=email, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Single User model for all roles.
    - Customers authenticate via phone
    - Staff/Admin authenticate via email
    Role controls what they can access.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Auth identifiers
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)

    # Profile
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    # Role & status
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Django admin access
    is_verified = models.BooleanField(default=False)  # Phone/email verified

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    # Customers log in via phone, staff via email
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        db_table = "accounts_users"
        indexes = [
            models.Index(fields=["phone"]),
            models.Index(fields=["email"]),
            models.Index(fields=["role"]),
        ]

    def __str__(self):
        return self.email or self.phone or str(self.id)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_customer(self):
        return self.role == Role.CUSTOMER

    @property
    def is_admin(self):
        return self.role == Role.ADMIN

    @property
    def is_ops_staff(self):
        return self.role == Role.OPS_STAFF

    @property
    def is_mover(self):
        return self.role == Role.MOVER