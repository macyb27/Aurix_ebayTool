"""Market Data Schemas."""

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class MarketDataRequest(BaseModel):
    """Request für Marktdaten."""

    category_id: str
    search_term: Optional[str] = None


class MarketDataResponse(BaseModel):
    """Market Data Response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: str
    search_term: Optional[str] = None
    avg_sold_price: Optional[Decimal] = None
    sold_count: Optional[int] = None
    active_listings: Optional[int] = None
    demand_score: Optional[Decimal] = None
