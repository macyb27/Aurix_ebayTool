"""Listing Service - Listing-Erstellung und -Verwaltung."""

import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.listing import Listing, ListingStatus
from app.models.product import Product
from app.services.ebay_service import EbayService

logger = logging.getLogger(__name__)


class ListingService:
    """Service für Listing-Orchestrierung."""

    def __init__(self, db: AsyncSession, ebay_service: EbayService | None = None):
        self._db = db
        self._ebay = ebay_service or EbayService()

    async def create_listing(
        self,
        *,
        title: str,
        description: str | None = None,
        price: float,
        quantity: int = 1,
        category_id: str | None = None,
        product_id: int | None = None,
        user_id: str,
    ) -> Listing:
        """Listing erstellen (Draft)."""
        listing = Listing(
            title=title,
            description=description,
            price=price,
            quantity=quantity,
            category_id=category_id,
            product_id=product_id,
            user_id=user_id,
            status=ListingStatus.DRAFT,
        )
        self._db.add(listing)
        await self._db.flush()
        await self._db.refresh(listing)
        return listing

    async def get_listing(self, listing_id: int, user_id: str | None = None) -> Listing | None:
        """Listing abrufen."""
        stmt = select(Listing).where(Listing.id == listing_id)
        if user_id:
            stmt = stmt.where(Listing.user_id == user_id)
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_listings(
        self,
        user_id: str,
        status: ListingStatus | None = None,
        limit: int = 50,
    ) -> list[Listing]:
        """Listings eines Users abrufen."""
        stmt = select(Listing).where(Listing.user_id == user_id)
        if status:
            stmt = stmt.where(Listing.status == status)
        stmt = stmt.order_by(Listing.created_at.desc()).limit(limit)
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def publish_to_ebay(self, listing_id: int, user_id: str) -> Listing:
        """Listing bei eBay publizieren."""
        listing = await self.get_listing(listing_id, user_id)
        if not listing:
            raise ValueError(f"Listing {listing_id} nicht gefunden")

        try:
            # Vereinfachte Integration - echte eBay Inventory API benötigt mehr Setup
            sku = f"AURIX-{listing_id}-{listing.user_id}"
            await self._ebay.create_inventory_item(
                sku=sku,
                payload={
                    "availability": {"shipToLocationAvailability": {"quantity": listing.quantity}},
                    "condition": "USED_EXCELLENT",
                    "product": {
                        "title": listing.title,
                        "description": listing.description or "",
                        "imageUrls": [],
                    },
                },
            )
            # In Produktion: Offer erstellen und publizieren
            listing.status = ListingStatus.ACTIVE
            listing.listed_at = datetime.now(timezone.utc)
        except Exception as e:
            listing.status = ListingStatus.FAILED
            listing.error_message = str(e)
            logger.exception("eBay publish failed for listing %s", listing_id)
            raise

        await self._db.flush()
        await self._db.refresh(listing)
        return listing

    async def update_status(self, listing_id: int, status: ListingStatus) -> Listing | None:
        """Listing-Status aktualisieren."""
        listing = await self.get_listing(listing_id)
        if not listing:
            return None
        listing.status = status
        await self._db.flush()
        await self._db.refresh(listing)
        return listing
