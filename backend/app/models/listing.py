"""Listing schema models."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, TenantMixin, UUIDMixin


class ListingTemplate(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """Listing template for reuse."""

    __tablename__ = "listing_templates"
    __table_args__ = {"schema": "public"}

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    title_template: Mapped[str | None] = mapped_column(Text, nullable=True)
    description_template: Mapped[str | None] = mapped_column(Text, nullable=True)
    default_duration: Mapped[str | None] = mapped_column(String(20), nullable=True)
    default_payment_methods: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    default_shipping_options: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class Listing(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """Listing (eBay item draft/published)."""

    __tablename__ = "listings"
    __table_args__ = {"schema": "public"}

    product_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    template_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("public.listing_templates.id"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    category_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    condition: Mapped[str | None] = mapped_column(String(50), nullable=True)
    images: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    duration: Mapped[str | None] = mapped_column(String(20), nullable=True)
    payment_methods: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    shipping_options: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    workflow_step: Mapped[str] = mapped_column(String(50), default="draft")
    created_by: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    approved_by: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    history = relationship("ListingHistory", back_populates="listing", cascade="all, delete-orphan")


class ListingHistory(Base, UUIDMixin):
    """Listing audit history."""

    __tablename__ = "listing_history"
    __table_args__ = {"schema": "public"}

    listing_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("public.listings.id"),
        nullable=False,
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
    )

    listing = relationship("Listing", back_populates="history")
