"""Market Service - Marktanalyse und Trends."""

import logging
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.market_data import MarketData
from app.services.ebay_service import EbayService

logger = logging.getLogger(__name__)


class MarketService:
    """Service für Marktanalyse und Trend-Daten."""

    def __init__(self, db: AsyncSession, ebay_service: EbayService | None = None):
        self._db = db
        self._ebay = ebay_service or EbayService()

    async def get_market_data(
        self,
        category_id: str,
        search_term: str | None = None,
    ) -> MarketData | None:
        """Marktdaten aus DB abrufen."""
        stmt = select(MarketData).where(MarketData.category_id == category_id)
        if search_term is not None:
            stmt = stmt.where(MarketData.search_term == search_term)
        stmt = stmt.order_by(MarketData.updated_at.desc()).limit(1)
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def fetch_and_store_market_data(
        self,
        category_id: str,
        search_term: str | None = None,
    ) -> MarketData:
        """Marktdaten von eBay holen und speichern."""
        ebay_data = await self._ebay.search_listings(
            query=search_term or "",
            category_ids=category_id,
            limit=100,
        )

        item_summaries = ebay_data.get("itemSummaries", [])
        prices = []
        for item in item_summaries:
            price = item.get("price", {}).get("value")
            if price:
                prices.append(Decimal(str(price)))

        avg_price = sum(prices) / len(prices) if prices else Decimal("0")
        min_price = min(prices) if prices else Decimal("0")
        max_price = max(prices) if prices else Decimal("0")

        market_data = MarketData(
            category_id=category_id,
            search_term=search_term,
            avg_sold_price=avg_price,
            sold_count=len(prices),
            active_listings=len(item_summaries),
            demand_score=avg_price * len(prices) / 100 if prices else None,
        )
        self._db.add(market_data)
        await self._db.flush()
        await self._db.refresh(market_data)
        return market_data

    async def get_category_trends(self, category_id: str) -> dict[str, Any]:
        """Trend-Daten für Kategorie."""
        data = await self.get_market_data(category_id)
        if data:
            return {
                "category_id": data.category_id,
                "avg_sold_price": float(data.avg_sold_price) if data.avg_sold_price else None,
                "sold_count": data.sold_count,
                "active_listings": data.active_listings,
                "demand_score": float(data.demand_score) if data.demand_score else None,
            }
        new_data = await self.fetch_and_store_market_data(category_id)
        return {
            "category_id": new_data.category_id,
            "avg_sold_price": float(new_data.avg_sold_price) if new_data.avg_sold_price else None,
            "sold_count": new_data.sold_count,
            "active_listings": new_data.active_listings,
            "demand_score": float(new_data.demand_score) if new_data.demand_score else None,
        }
