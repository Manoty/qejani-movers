# backend/apps/pricing/views.py

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.pricing.data_classes import QuoteRequest
from apps.pricing.engine import PricingEngine, PricingEngineError
from apps.pricing.models import AddOnService, HouseSizePricing
from apps.pricing.serializers import (
    AddOnServiceSerializer,
    HouseSizePricingSerializer,
    QuoteRequestSerializer,
)


@api_view(["POST"])
@permission_classes([AllowAny])
def estimate_quote(request):
    """
    Compute a moving quote from the provided inputs.
    Returns an itemized breakdown. Does NOT save anything — pure calculation.
    Call this from the frontend quote estimator before the customer books.
    """
    serializer = QuoteRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    quote_request = QuoteRequest(**serializer.validated_data)

    try:
        result = PricingEngine.calculate(quote_request)
    except PricingEngineError as e:
        return Response({"detail": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    return Response(result.to_dict(), status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([AllowAny])
def list_addons(request):
    """Return all active add-on services. Used to populate the quote estimator UI."""
    addons = AddOnService.objects.filter(is_active=True).order_by("name")
    serializer = AddOnServiceSerializer(addons, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def list_house_sizes(request):
    """Return all active house size options with their base prices."""
    sizes = HouseSizePricing.objects.filter(is_active=True).order_by("base_price")
    serializer = HouseSizePricingSerializer(sizes, many=True)
    return Response(serializer.data)