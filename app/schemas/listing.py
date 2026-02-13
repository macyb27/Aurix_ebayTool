"""Listing Schemas."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.listing import ListingStatus


class ListingBase(BaseModel):
    """Basis Listing Schema."""

    title: str
    description: Optional[str] = None
    price: Decimal
    quantity: int = 1
    category_id: Optional[str] = None
    listing_type: str = "FixedPrice"
    duration: str = "GTC"


class ListingCreate(ListingBase):
    """Listing Erstellung."""

    product_id: Optional[int] = None
    user_id: str


class ListingUpdate(BaseModel):
    """Listing Update (partial)."""

    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    quantity: Optional[int] = None
    category_id: Optional[str] = None
    status: Optional[ListingStatus] = None


class ListingResponse(ListingBase):
    """Listing Response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: Optional[int] = None
    user_id: str
    ebay_item_id: Optional[str] = None
    status: ListingStatus
    error_message: Optional[str] = None
    listed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
