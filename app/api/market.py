"""Market API Endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.market import MarketDataRequest
from app.services.market_service import MarketService

router = APIRouter()


@router.get("/trends/{category_id}")
async def get_category_trends(
    category_id: str,
    search_term: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Markttrends für Kategorie abrufen."""
    service = MarketService(db)
    return await service.get_category_trends(category_id)


@router.post("/fetch")
async def fetch_market_data(
    data: MarketDataRequest,
    db: AsyncSession = Depends(get_db),
):
    """Marktdaten von eBay holen und speichern."""
    service = MarketService(db)
    market_data = await service.fetch_and_store_market_data(
        category_id=data.category_id,
        search_term=data.search_term,
    )
    return {
        "id": market_data.id,
        "category_id": market_data.category_id,
        "avg_sold_price": float(market_data.avg_sold_price) if market_data.avg_sold_price else None,
        "sold_count": market_data.sold_count,
        "active_listings": market_data.active_listings,
    }
