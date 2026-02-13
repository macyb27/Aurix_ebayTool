"""Unit-Tests für MarketService."""

import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.market_data import MarketData
from app.services.market_service import MarketService


@pytest.mark.asyncio
async def test_get_market_data_empty(db_session: AsyncSession):
    """Leere DB liefert None."""
    service = MarketService(db_session)
    result = await service.get_market_data("9355")
    assert result is None


@pytest.mark.asyncio
async def test_fetch_and_store_market_data(db_session: AsyncSession):
    """Marktdaten werden von eBay geholt und gespeichert."""
    mock_ebay = MagicMock()
    mock_ebay.search_listings = AsyncMock(return_value={
        "itemSummaries": [
            {"price": {"value": "10.00"}},
            {"price": {"value": "20.00"}},
            {"price": {"value": "30.00"}},
        ]
    })

    service = MarketService(db_session, ebay_service=mock_ebay)
    result = await service.fetch_and_store_market_data("9355", "laptop")

    assert result.category_id == "9355"
    assert result.search_term == "laptop"
    assert result.avg_sold_price == Decimal("20")
    assert result.sold_count == 3
    await db_session.rollback()
