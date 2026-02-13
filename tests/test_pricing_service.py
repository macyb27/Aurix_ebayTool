"""Unit-Tests für PricingService."""

import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.pricing_service import PricingService


@pytest.mark.asyncio
async def test_get_pricing_empty(db_session: AsyncSession):
    """Leere DB liefert None."""
    service = PricingService(db_session)
    result = await service.get_pricing(category_id="9355")
    assert result is None


@pytest.mark.asyncio
async def test_calculate_price_from_ebay(db_session: AsyncSession):
    """Preis wird aus eBay-Daten berechnet."""
    mock_ebay = MagicMock()
    mock_ebay.search_listings = AsyncMock(return_value={
        "itemSummaries": [
            {"price": {"value": "100.00"}},
            {"price": {"value": "120.00"}},
            {"price": {"value": "80.00"}},
        ]
    })

    service = PricingService(db_session, ebay_service=mock_ebay)
    result = await service.calculate_price(
        search_query="laptop",
        category_id="9355",
    )

    assert result["avg_price"] == 100.0
    assert result["min_price"] == 80.0
    assert result["max_price"] == 120.0
    assert result["sample_count"] == 3
    assert "recommended_price" in result
    assert result["recommended_price"] == 95.0  # 95% von 100
    await db_session.rollback()


@pytest.mark.asyncio
async def test_calculate_price_empty_results(db_session: AsyncSession):
    """Leere eBay-Ergebnisse liefern Nullen."""
    mock_ebay = MagicMock()
    mock_ebay.search_listings = AsyncMock(return_value={"itemSummaries": []})

    service = PricingService(db_session, ebay_service=mock_ebay)
    result = await service.calculate_price(search_query="xyznonexistent")

    assert result["avg_price"] == 0.0
    assert result["sample_count"] == 0
