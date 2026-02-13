"""Pricing Schemas."""

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PricingRequest(BaseModel):
    """Request für Preisanfrage."""

    category_id: Optional[str] = None
    search_query: Optional[str] = None
    product_id: Optional[int] = None


class PricingResponse(BaseModel):
    """Pricing Response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: Optional[int] = None
    category_id: Optional[str] = None
    search_query: Optional[str] = None
    avg_price: Decimal
    min_price: Decimal
    max_price: Decimal
    sample_count: int
