"""eBay/Sync schema models."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TenantMixin, UUIDMixin


class EbayAccount(Base, UUIDMixin, TenantMixin):
    """eBay OAuth account credentials."""

    __tablename__ = "ebay_accounts"
    __table_args__ = {"schema": "public"}

    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    ebay_user_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    access_token_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    refresh_token_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    token_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    marketplace: Mapped[str] = mapped_column(String(20), default="EBAY_DE")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class SyncJob(Base, UUIDMixin):
    """Sync job for publishing to eBay."""

    __tablename__ = "sync_jobs"
    __table_args__ = {"schema": "public"}

    listing_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    ebay_account_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("public.ebay_accounts.id"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="queued")
    ebay_item_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ebay_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    request_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    response_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class EbayListingMapping(Base):
    """Mapping listing_id to ebay_item_id."""

    __tablename__ = "ebay_listing_mappings"
    __table_args__ = {"schema": "public"}

    listing_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, nullable=False
    )
    ebay_item_id: Mapped[str] = mapped_column(String(50), nullable=False)
    ebay_account_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("public.ebay_accounts.id"),
        nullable=False,
    )
    last_sync_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
