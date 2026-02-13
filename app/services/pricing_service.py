"""Pricing Service - Preiskalkulation und Wettbewerbsanalyse."""

import logging
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.pricing import PricingHistory
from app.services.ebay_service import EbayService

logger = logging.getLogger(__name__)


class PricingService:
    """Service für Preiskalkulation."""

    def __init__(self, db: AsyncSession, ebay_service: EbayService | None = None):
        self._db = db
        self._ebay = ebay_service or EbayService()

    async def get_pricing(
        self,
        *,
        category_id: str | None = None,
        search_query: str | None = None,
        product_id: int | None = None,
    ) -> PricingHistory | None:
        """Preisdaten aus DB abrufen."""
        stmt = select(PricingHistory)
        if category_id:
            stmt = stmt.where(PricingHistory.category_id == category_id)
        if search_query:
            stmt = stmt.where(PricingHistory.search_query == search_query)
        if product_id:
            stmt = stmt.where(PricingHistory.product_id == product_id)
        stmt = stmt.order_by(PricingHistory.updated_at.desc()).limit(1)
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def calculate_price(
        self,
        *,
        category_id: str | None = None,
        search_query: str | None = None,
        product_id: int | None = None,
    ) -> dict[str, Any]:
        """Preisempfehlung berechnen basierend auf eBay-Daten."""
        existing = await self.get_pricing(
            category_id=category_id,
            search_query=search_query,
            product_id=product_id,
        )
        if existing:
            return {
                "avg_price": float(existing.avg_price),
                "min_price": float(existing.min_price),
                "max_price": float(existing.max_price),
                "sample_count": existing.sample_count,
                "recommended_price": float(existing.avg_price) * 0.95,
            }

        query = search_query or "product"
        ebay_data = await self._ebay.search_listings(
            query=query,
            category_ids=category_id,
            limit=50,
        )

        item_summaries = ebay_data.get("itemSummaries", [])
        prices = []
        for item in item_summaries:
            price = item.get("price", {}).get("value")
            if price:
                prices.append(Decimal(str(price)))

        if not prices:
            return {
                "avg_price": 0.0,
                "min_price": 0.0,
                "max_price": 0.0,
                "sample_count": 0,
                "recommended_price": 0.0,
            }

        avg_price = sum(prices) / len(prices)
        min_price = min(prices)
        max_price = max(prices)

        pricing = PricingHistory(
            product_id=product_id,
            category_id=category_id,
            search_query=search_query,
            avg_price=avg_price,
            min_price=min_price,
            max_price=max_price,
            sample_count=len(prices),
        )
        self._db.add(pricing)
        await self._db.flush()

        recommended = avg_price * Decimal("0.95")

        return {
            "avg_price": float(avg_price),
            "min_price": float(min_price),
            "max_price": float(max_price),
            "sample_count": len(prices),
            "recommended_price": float(recommended),
        }
