"""Pricing API router."""

from fastapi import APIRouter, Depends

from app.api.deps import get_pricing_service
from app.core.database import DbSession
from app.schemas.pricing import PriceSuggestionRequest, PriceSuggestionResponse
from app.services.pricing_service import PricingService

router = APIRouter(prefix="/pricing", tags=["Pricing"])


@router.post("/suggest", response_model=PriceSuggestionResponse)
async def suggest_price(
    body: PriceSuggestionRequest,
):
    """Get price suggestion for listing."""
    service = get_pricing_service()
    return service.suggest_price(
        base_price=body.basePrice,
        category_id=body.categoryId,
        condition=body.condition,
    )
