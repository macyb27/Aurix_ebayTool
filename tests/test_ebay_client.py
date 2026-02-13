"""Unit-Tests für EbayApiClient."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.core.ebay_client import EbayApiClient
from app.core.exceptions import EbayApiError, EbayRateLimitError, EbayTokenError


@pytest.mark.asyncio
async def test_get_client_token_success():
    """Token wird erfolgreich abgerufen."""
    with patch("app.core.ebay_client.httpx.AsyncClient") as mock_client_cls:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test-token",
            "expires_in": 7200,
        }

        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_cls.return_value = mock_client

        client = EbayApiClient(app_id="test", cert_id="test")
        token = await client.get_client_token()

        assert token == "test-token"


@pytest.mark.asyncio
async def test_get_client_token_failure():
    """Token-Fehler wird geworfen."""
    with patch("app.core.ebay_client.httpx.AsyncClient") as mock_client_cls:
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"

        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_cls.return_value = mock_client

        client = EbayApiClient(app_id="test", cert_id="test")

        with pytest.raises(EbayTokenError, match="Token request failed"):
            await client.get_client_token()


def test_raise_for_status_429():
    """429 wirft EbayRateLimitError."""
    client = EbayApiClient()
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.text = "Rate limited"

    with pytest.raises(EbayRateLimitError):
        client._raise_for_status(mock_response)


def test_raise_for_status_500():
    """5xx wirft EbayApiError."""
    client = EbayApiClient()
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Server error"

    with pytest.raises(EbayApiError):
        client._raise_for_status(mock_response)
