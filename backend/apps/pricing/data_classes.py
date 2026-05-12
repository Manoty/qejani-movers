# backend/apps/pricing/data_classes.py

from dataclasses import dataclass, field
from decimal import Decimal
from typing import List


@dataclass
class QuoteRequest:
    """
    All inputs needed to compute a moving quote.
    Distance is in kilometres.
    Floor number is used for staircase calculation.
    """
    house_size: str          # HouseSize choice value
    distance_km: float       # Distance from pickup to destination
    floor_number: int        # Floor of pickup location (ground = 1)
    has_lift: bool           # Lift available at pickup building?
    addon_ids: List[str]     # List of AddOnService UUIDs selected


@dataclass
class QuoteLineItem:
    """A single priced component in the quote breakdown."""
    label: str
    amount: Decimal


@dataclass
class QuoteResult:
    """
    Full output of the pricing engine.
    Contains itemized breakdown + total.
    Snapshot this into a Booking when confirmed.
    """
    base_price: Decimal
    distance_surcharge: Decimal
    staircase_fee: Decimal
    addons_total: Decimal
    total: Decimal
    line_items: List[QuoteLineItem] = field(default_factory=list)
    currency: str = "KES"

    def to_dict(self) -> dict:
        return {
            "base_price": str(self.base_price),
            "distance_surcharge": str(self.distance_surcharge),
            "staircase_fee": str(self.staircase_fee),
            "addons_total": str(self.addons_total),
            "total": str(self.total),
            "currency": self.currency,
            "line_items": [
                {"label": item.label, "amount": str(item.amount)}
                for item in self.line_items
            ],
        }