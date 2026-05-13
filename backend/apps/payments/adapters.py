# backend/apps/payments/adapters.py

import base64
import logging
import requests
from dataclasses import dataclass
from datetime import datetime
from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class STKPushResult:
    """Structured result from an STK Push initiation."""
    success: bool
    checkout_request_id: str = ""
    merchant_request_id: str = ""
    response_code: str = ""
    response_description: str = ""
    customer_message: str = ""
    error: str = ""


class MpesaAdapter:
    """
    Isolated Safaricom Daraja API client.

    This class is the single boundary between our system and Safaricom.
    All other code depends on this interface — never on Safaricom directly.

    To mock in tests: replace this class with a stub that returns
    STKPushResult objects. No HTTP calls needed in tests.

    Credentials read from settings — never hardcoded.
    """

    BASE_URL = "https://sandbox.safaricom.co.ke"  # Swap for prod

    def __init__(self):
        self.consumer_key    = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.shortcode       = settings.MPESA_SHORTCODE
        self.passkey         = settings.MPESA_PASSKEY
        self.callback_url    = settings.MPESA_CALLBACK_URL

    def _get_access_token(self) -> str:
        """
        Fetch a short-lived OAuth token from Safaricom.
        In production, cache this token for its ~1hr lifetime.
        For MVP: fetch fresh per request (simple, slightly slower).
        """
        credentials = base64.b64encode(
            f"{self.consumer_key}:{self.consumer_secret}".encode()
        ).decode()

        response = requests.get(
            f"{self.BASE_URL}/oauth/v1/generate?grant_type=client_credentials",
            headers={"Authorization": f"Basic {credentials}"},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()["access_token"]

    def _generate_password(self, timestamp: str) -> str:
        """
        Safaricom STK Push password:
        Base64(Shortcode + Passkey + Timestamp)
        """
        raw = f"{self.shortcode}{self.passkey}{timestamp}"
        return base64.b64encode(raw.encode()).decode()

    def initiate_stk_push(self, phone: str, amount: int, reference: str, description: str) -> STKPushResult:
        """
        Send STK Push prompt to customer's phone.

        Args:
            phone: Safaricom format — 2547XXXXXXXX (no +)
            amount: Integer Kenya shillings (no decimals)
            reference: Shown to customer on M-Pesa prompt
            description: Transaction description

        Returns:
            STKPushResult with success flag and Safaricom IDs
        """
        try:
            token = self._get_access_token()
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            password = self._generate_password(timestamp)

            payload = {
                "BusinessShortCode": self.shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": amount,
                "PartyA": phone,
                "PartyB": self.shortcode,
                "PhoneNumber": phone,
                "CallBackURL": self.callback_url,
                "AccountReference": reference,
                "TransactionDesc": description,
            }

            response = requests.post(
                f"{self.BASE_URL}/mpesa/stkpush/v1/processrequest",
                json=payload,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                timeout=15,
            )
            data = response.json()

            if data.get("ResponseCode") == "0":
                return STKPushResult(
                    success=True,
                    checkout_request_id=data["CheckoutRequestID"],
                    merchant_request_id=data["MerchantRequestID"],
                    response_code=data["ResponseCode"],
                    response_description=data.get("ResponseDescription", ""),
                    customer_message=data.get("CustomerMessage", ""),
                )

            return STKPushResult(
                success=False,
                response_code=data.get("ResponseCode", ""),
                response_description=data.get("ResponseDescription", ""),
                error=data.get("errorMessage", "STK Push initiation failed."),
            )

        except requests.RequestException as e:
            logger.error("M-Pesa STK Push network error", exc_info=True)
            return STKPushResult(success=False, error=str(e))

    @staticmethod
    def normalize_phone(phone: str) -> str:
        """
        Convert Kenyan phone formats to Safaricom's required format.
        +254712345678 → 254712345678
        07XXXXXXXX   → 254712345678
        """
        phone = phone.strip().replace(" ", "")
        if phone.startswith("+"):
            return phone[1:]
        if phone.startswith("07") or phone.startswith("01"):
            return "254" + phone[1:]
        return phone