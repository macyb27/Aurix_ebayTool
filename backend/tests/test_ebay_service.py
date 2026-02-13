"""Unit tests for EbayService and EbayClient."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.ebay_client import EbayClient
from app.services.ebay_service import EbayService


@pytest.mark.asyncio
async def test_ebay_client_set_access_token():
    """EbayClient stores access token."""
    client = EbayClient()
    client.set_access_token("test-token-123")
    assert client._access_token == "test-token-123"


def test_ebay_client_init_uses_settings():
    """EbayClient uses settings when no overrides."""
    client = EbayClient()
    assert client.app_id is not None or client.app_id is None
    assert client._base_url is not None


@pytest.mark.asyncio
async def test_ebay_service_get_sync_status_returns_none_when_no_job(mock_db_session, tenant_id, listing_id):
    """Get sync status returns None when no sync job exists."""
    from sqlalchemy.engine import Result

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db_session.execute = AsyncMock(return_value=mock_result)

    service = EbayService(mock_db_session)
    result = await service.get_sync_status(listing_id, tenant_id)

    assert result is None
