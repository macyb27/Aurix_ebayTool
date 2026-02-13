"""Product Schemas."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ProductBase(BaseModel):
    """Basis Product Schema."""

    title: str
    description: Optional[str] = None
    category_id: Optional[str] = None
    brand: Optional[str] = None
    condition: Optional[str] = None
    suggested_price: Optional[Decimal] = None
    image_url: Optional[str] = None


class ProductCreate(ProductBase):
    """Product Erstellung."""

    user_id: Optional[str] = None


class ProductUpdate(BaseModel):
    """Product Update (partial)."""

    title: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[str] = None
    brand: Optional[str] = None
    condition: Optional[str] = None
    suggested_price: Optional[Decimal] = None
    image_url: Optional[str] = None


class ProductResponse(ProductBase):
    """Product Response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[str] = None
    vision_analysis: Optional[str] = None
    created_at: datetime
    updated_at: datetime
