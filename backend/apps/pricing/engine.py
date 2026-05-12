# backend/apps/pricing/engine.py

from decimal import Decimal
from typing import List

from apps.pricing.data_classes import QuoteLineItem, QuoteRequest, QuoteResult
from apps.pricing.models import AddOnService, DistanceTier, HouseSizePricing


STAIRCASE_FEE_PER_FLOOR = Decimal("1500.00")
STAIRCASE_FREE_FLOORS = 3  # Floors ≤ this are free (no staircase surcharge)


class PricingEngineError(Exception):
    """Raised when the engine cannot compute a quote due to missing config."""
    pass


class PricingEngine:
    """
    Stateless pricing calculator.

    Usage:
        request = QuoteRequest(...)
        result = PricingEngine.calculate(request)

    All pricing data is read from the database at call time.
    No state is stored on the class — safe for concurrent use.
    """

    @staticmethod
    def calculate(request: QuoteRequest) -> QuoteResult:
        line_items: List[QuoteLineItem] = []

        # ── 1. Base price ─────────────────────────────────────────────
        base_price = PricingEngine._get_base_price(request.house_size)
        line_items.append(QuoteLineItem(
            label=f"Base rate ({request.house_size.replace('_', ' ').title()})",
            amount=base_price,
        ))

        # ── 2. Distance surcharge ──────────────────────────────────────
        distance_surcharge = PricingEngine._get_distance_surcharge(request.distance_km)
        if distance_surcharge > 0:
            line_items.append(QuoteLineItem(
                label=f"Distance surcharge ({request.distance_km:.1f} km)",
                amount=distance_surcharge,
            ))

        # ── 3. Staircase fee ───────────────────────────────────────────
        staircase_fee = PricingEngine._get_staircase_fee(
            floor_number=request.floor_number,
            has_lift=request.has_lift,
        )
        if staircase_fee > 0:
            chargeable_floors = request.floor_number - STAIRCASE_FREE_FLOORS
            line_items.append(QuoteLineItem(
                label=f"Staircase fee ({chargeable_floors} floor(s) above floor {STAIRCASE_FREE_FLOORS})",
                amount=staircase_fee,
            ))

        # ── 4. Add-ons ─────────────────────────────────────────────────
        addons_total, addon_items = PricingEngine._get_addons_total(request.addon_ids)
        line_items.extend(addon_items)

        # ── 5. Total ───────────────────────────────────────────────────
        total = base_price + distance_surcharge + staircase_fee + addons_total

        return QuoteResult(
            base_price=base_price,
            distance_surcharge=distance_surcharge,
            staircase_fee=staircase_fee,
            addons_total=addons_total,
            total=total,
            line_items=line_items,
        )

    @staticmethod
    def _get_base_price(house_size: str) -> Decimal:
        try:
            pricing = HouseSizePricing.objects.get(house_size=house_size, is_active=True)
            return Decimal(str(pricing.base_price))
        except HouseSizePricing.DoesNotExist:
            raise PricingEngineError(
                f"No active base pricing found for house size: {house_size}. "
                "An admin must configure pricing before quotes can be generated."
            )

    @staticmethod
    def _get_distance_surcharge(distance_km: float) -> Decimal:
        """
        Find the matching distance tier and return its surcharge.
        Tiers are ordered by min_km ascending.
        A tier with null max_km covers everything above its min_km.
        """
        tiers = DistanceTier.objects.filter(is_active=True).order_by("min_km")

        for tier in tiers:
            lower_match = distance_km >= tier.min_km
            upper_match = tier.max_km is None or distance_km < tier.max_km
            if lower_match and upper_match:
                return Decimal(str(tier.surcharge))

        # If no tier matched, distance falls outside all configured ranges.
        # Return 0 rather than crashing — ops can handle edge cases manually.
        return Decimal("0.00")

    @staticmethod
    def _get_staircase_fee(floor_number: int, has_lift: bool) -> Decimal:
        """
        Staircase fee applies only when:
        - No lift is available, AND
        - The floor is above STAIRCASE_FREE_FLOORS (default: 3)

        Fee = (floor_number - STAIRCASE_FREE_FLOORS) × STAIRCASE_FEE_PER_FLOOR
        """
        if has_lift or floor_number <= STAIRCASE_FREE_FLOORS:
            return Decimal("0.00")

        chargeable_floors = floor_number - STAIRCASE_FREE_FLOORS
        return Decimal(str(chargeable_floors)) * STAIRCASE_FEE_PER_FLOOR

    @staticmethod
    def _get_addons_total(addon_ids: List[str]):
        """
        Fetch requested add-ons from DB, sum their prices.
        Silently ignores invalid/inactive IDs — they won't appear in the quote.
        Returns (total, list_of_line_items).
        """
        if not addon_ids:
            return Decimal("0.00"), []

        addons = AddOnService.objects.filter(id__in=addon_ids, is_active=True)
        items = []
        total = Decimal("0.00")

        for addon in addons:
            price = Decimal(str(addon.price))
            total += price
            items.append(QuoteLineItem(label=f"Add-on: {addon.name}", amount=price))

        return total, items