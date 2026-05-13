# backend/apps/bookings/permissions.py

from rest_framework.permissions import BasePermission
from apps.accounts.models import Role


class IsCustomer(BasePermission):
    """Allow access only to users with CUSTOMER role."""
    message = "Only customers can perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == Role.CUSTOMER
        )


class IsOpsOrAdmin(BasePermission):
    """Allow access to ops staff or admins."""
    message = "Only operations staff or admins can perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in [Role.ADMIN, Role.OPS_STAFF]
        )


class IsBookingOwner(BasePermission):
    """Object-level: only the booking's customer can access it."""
    message = "You do not have permission to access this booking."

    def has_object_permission(self, request, view, obj):
        return obj.customer_id == request.user.id