"""Unit tests for MarketService."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.inventory import Category
from app.services.market_service import MarketService


@pytest.mark.asyncio
async def test_get_categories_returns_empty_list(mock_db_session, tenant_id):
    """Get categories returns empty list when no categories."""
    from sqlalchemy.engine import Result

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db_session.execute = AsyncMock(return_value=mock_result)

    service = MarketService(mock_db_session)
    result = await service.get_categories(tenant_id)

    assert result == []


@pytest.mark.asyncio
async def test_suggest_price_is_on_pricing_service():
    """PricingService has suggest_price (smoke test)."""
    from app.services.pricing_service import PricingService

    service = PricingService()
    result = service.suggest_price(base_price=29.99, condition="new")

    assert "suggestedPrice" in result
    assert result["suggestedPrice"] >= result["minPrice"]
