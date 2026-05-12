# backend/apps/accounts/tests/test_auth.py

import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from apps.accounts.models import User, Role


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def customer_payload():
    return {
        "phone": "+254712345678",
        "password": "StrongPass123",
        "first_name": "Jane",
        "last_name": "Wanjiru",
    }


@pytest.mark.django_db
class TestCustomerRegistration:
    def test_register_success(self, api_client, customer_payload):
        response = api_client.post(
            reverse("customer-register"), customer_payload, format="json"
        )
        assert response.status_code == 201
        assert "tokens" in response.data
        assert response.data["user"]["phone"] == "+254712345678"
        assert response.data["user"]["role"] == Role.CUSTOMER

    def test_register_duplicate_phone(self, api_client, customer_payload):
        api_client.post(reverse("customer-register"), customer_payload, format="json")
        response = api_client.post(reverse("customer-register"), customer_payload, format="json")
        assert response.status_code == 400

    def test_register_invalid_phone(self, api_client, customer_payload):
        customer_payload["phone"] = "12345"
        response = api_client.post(reverse("customer-register"), customer_payload, format="json")
        assert response.status_code == 400

    def test_register_short_password(self, api_client, customer_payload):
        customer_payload["password"] = "short"
        response = api_client.post(reverse("customer-register"), customer_payload, format="json")
        assert response.status_code == 400


@pytest.mark.django_db
class TestCustomerLogin:
    def test_login_success(self, api_client, customer_payload):
        api_client.post(reverse("customer-register"), customer_payload, format="json")
        response = api_client.post(
            reverse("customer-login"),
            {"phone": customer_payload["phone"], "password": customer_payload["password"]},
            format="json",
        )
        assert response.status_code == 200
        assert "access" in response.data["tokens"]

    def test_login_wrong_password(self, api_client, customer_payload):
        api_client.post(reverse("customer-register"), customer_payload, format="json")
        response = api_client.post(
            reverse("customer-login"),
            {"phone": customer_payload["phone"], "password": "wrongpassword"},
            format="json",
        )
        assert response.status_code == 401

    def test_login_nonexistent_phone(self, api_client):
        response = api_client.post(
            reverse("customer-login"),
            {"phone": "+254799999999", "password": "anything"},
            format="json",
        )
        assert response.status_code == 401


@pytest.mark.django_db
class TestProfileEndpoint:
    def test_get_profile_authenticated(self, api_client, customer_payload):
        reg = api_client.post(reverse("customer-register"), customer_payload, format="json")
        token = reg.data["tokens"]["access"]
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = api_client.get(reverse("profile"))
        assert response.status_code == 200
        assert response.data["phone"] == customer_payload["phone"]

    def test_get_profile_unauthenticated(self, api_client):
        response = api_client.get(reverse("profile"))
        assert response.status_code == 401