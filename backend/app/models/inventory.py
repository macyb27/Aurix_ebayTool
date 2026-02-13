"""Inventory schema models."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, TenantMixin, UUIDMixin


class Category(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """Product category with eBay mapping."""

    __tablename__ = "categories"
    __table_args__ = {"schema": "public"}

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("public.categories.id"),
        nullable=True,
    )
    ebay_category_id: Mapped[str | None] = mapped_column(String(50), nullable=True)


class Product(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """Product master data."""

    __tablename__ = "products"
    __table_args__ = {"schema": "public"}

    sku: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("public.categories.id"),
        nullable=True,
    )
    images: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    attributes: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    variants = relationship("Variant", back_populates="product", cascade="all, delete-orphan")


class Variant(Base, UUIDMixin, TimestampMixin):
    """Product variant (size, color, etc.)."""

    __tablename__ = "variants"
    __table_args__ = {"schema": "public"}

    product_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("public.products.id"),
        nullable=False,
    )
    sku: Mapped[str] = mapped_column(String(100), nullable=False)
    attributes: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    product = relationship("Product", back_populates="variants")


class StockMovement(Base, UUIDMixin):
    """Stock movement audit log."""

    __tablename__ = "stock_movements"
    __table_args__ = {"schema": "public"}

    variant_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("public.variants.id"),
        nullable=False,
    )
    quantity_delta: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity_after: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str | None] = mapped_column(String(50), nullable=True)
    reference_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
    )
