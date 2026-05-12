# backend/apps/accounts/urls.py

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from apps.accounts import views

urlpatterns = [
    # Customer auth
    path("customers/register/", views.customer_register, name="customer-register"),
    path("customers/login/", views.customer_login, name="customer-login"),

    # Staff auth
    path("staff/register/", views.staff_register, name="staff-register"),
    path("staff/login/", views.staff_login, name="staff-login"),

    # JWT refresh (shared)
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),

    # Profile
    path("me/", views.profile, name="profile"),
]