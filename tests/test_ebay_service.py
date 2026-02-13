"""Unit-Tests für EbayService."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.ebay_service import EbayService
from app.core.exceptions import EbayApiError, EbayRateLimitError


@pytest.mark.asyncio
async def test_search_listings_success():
    """Suche liefert Ergebnisse."""
    mock_client = MagicMock()
    mock_client.get = AsyncMock(return_value={
        "itemSummaries": [
            {"itemId": "123", "price": {"value": "29.99"}},
            {"itemId": "456", "price": {"value": "34.99"}},
        ]
    })

    service = EbayService(client=mock_client)

    result = await service.search_listings("laptop")

    assert "itemSummaries" in result
    assert len(result["itemSummaries"]) == 2
    mock_client.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_item_success():
    """Einzelnes Item abrufen."""
    mock_client = MagicMock()
    mock_client.get = AsyncMock(return_value={"itemId": "123", "title": "Test Item"})

    service = EbayService(client=mock_client)

    result = await service.get_item("123")

    assert result["itemId"] == "123"
    assert result["title"] == "Test Item"


@pytest.mark.asyncio
async def test_get_category_tree():
    """Kategorie-Baum abrufen."""
    mock_client = MagicMock()
    mock_client.get = AsyncMock(return_value={"categoryTreeNode": {"id": "0"}})

    service = EbayService(client=mock_client)

    result = await service.get_category_tree()

    assert "categoryTreeNode" in result
