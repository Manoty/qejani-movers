# backend/apps/accounts/views.py

from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.serializers import (
    CustomerRegisterSerializer,
    StaffRegisterSerializer,
    CustomerLoginSerializer,
    StaffLoginSerializer,
    UserProfileSerializer,
)
from apps.accounts.services import CustomerRegistrationService, StaffRegistrationService


def get_tokens_for_user(user):
    """
    Generate JWT access + refresh tokens for a given user.
    Centralized here so token generation is consistent across views.
    """
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


@api_view(["POST"])
@permission_classes([AllowAny])
def customer_register(request):
    """Register a new customer account."""
    serializer = CustomerRegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        user = CustomerRegistrationService.register(**serializer.validated_data)
    except ValidationError as e:
        return Response(e.message_dict, status=status.HTTP_400_BAD_REQUEST)

    tokens = get_tokens_for_user(user)
    profile = UserProfileSerializer(user).data

    return Response(
        {"user": profile, "tokens": tokens},
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def customer_login(request):
    """Login for customers using phone + password."""
    serializer = CustomerLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    phone = serializer.validated_data["phone"]
    password = serializer.validated_data["password"]

    # Django's authenticate uses USERNAME_FIELD (email).
    # For phone login we fetch the user manually then verify password.
    from apps.accounts.models import User
    try:
        user = User.objects.get(phone=phone)
    except User.DoesNotExist:
        return Response(
            {"detail": "Invalid phone number or password."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not user.check_password(password):
        return Response(
            {"detail": "Invalid phone number or password."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not user.is_active:
        return Response(
            {"detail": "Account is deactivated."},
            status=status.HTTP_403_FORBIDDEN,
        )

    tokens = get_tokens_for_user(user)
    profile = UserProfileSerializer(user).data

    return Response({"user": profile, "tokens": tokens})


@api_view(["POST"])
@permission_classes([AllowAny])
def staff_login(request):
    """Login for staff/admin using email + password."""
    serializer = StaffLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = authenticate(
        request,
        username=serializer.validated_data["email"],
        password=serializer.validated_data["password"],
    )

    if not user:
        return Response(
            {"detail": "Invalid email or password."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if user.is_customer:
        return Response(
            {"detail": "Use the customer login endpoint."},
            status=status.HTTP_403_FORBIDDEN,
        )

    tokens = get_tokens_for_user(user)
    profile = UserProfileSerializer(user).data

    return Response({"user": profile, "tokens": tokens})


@api_view(["POST"])
@permission_classes([IsAdminUser])
def staff_register(request):
    """
    Create a staff/admin account.
    Only callable by existing admins (IsAdminUser enforces this).
    """
    serializer = StaffRegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        user = StaffRegistrationService.register(**serializer.validated_data)
    except ValidationError as e:
        return Response(e.message_dict, status=status.HTTP_400_BAD_REQUEST)

    profile = UserProfileSerializer(user).data
    return Response(profile, status=status.HTTP_201_CREATED)


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def profile(request):
    """Get or update the authenticated user's profile."""
    if request.method == "GET":
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)