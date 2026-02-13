"""Listing Model für eBay Listings."""

import enum
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    Numeric,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin


class ListingStatus(str, enum.Enum):
    """Status eines Listings."""

    DRAFT = "draft"
    PENDING = "pending"
    ACTIVE = "active"
    ENDED = "ended"
    SOLD = "sold"
    CANCELLED = "cancelled"
    FAILED = "failed"


class Listing(Base, TimestampMixin):
    """eBay Listing Entität."""

    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=True, index=True
    )
    user_id: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    ebay_item_id: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    category_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[ListingStatus] = mapped_column(
        Enum(ListingStatus), default=ListingStatus.DRAFT
    )
    listing_type: Mapped[str] = mapped_column(String(50), default="FixedPrice")
    duration: Mapped[str] = mapped_column(String(20), default="GTC")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    listed_at: Mapped[object | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
