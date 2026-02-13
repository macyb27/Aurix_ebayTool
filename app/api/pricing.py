"""Pricing API Endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.pricing import PricingRequest
from app.services.pricing_service import PricingService

router = APIRouter()


@router.post("/calculate")
async def calculate_price(
    data: PricingRequest,
    db: AsyncSession = Depends(get_db),
):
    """Preisempfehlung berechnen."""
    service = PricingService(db)
    result = await service.calculate_price(
        category_id=data.category_id,
        search_query=data.search_query,
        product_id=data.product_id,
    )
    return result
