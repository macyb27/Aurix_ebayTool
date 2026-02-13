"""Unit tests for EbayClient retry and error handling."""

from unittest.mock import MagicMock, patch

import httpx
import pytest

from app.core.exceptions import EbayApiError, EbayRateLimitError
from app.services.ebay_client import EbayClient, _is_retryable


def test_is_retryable_rate_limit():
    """Rate limit error is retryable."""
    assert _is_retryable(EbayRateLimitError()) is True


def test_is_retryable_5xx():
    """5xx HTTP error is retryable."""
    resp = httpx.Response(503, text="Service Unavailable")
    exc = httpx.HTTPStatusError("503", request=MagicMock(), response=resp)
    assert _is_retryable(exc) is True


def test_is_retryable_429():
    """429 is retryable."""
    resp = httpx.Response(429, text="Too Many Requests")
    exc = httpx.HTTPStatusError("429", request=MagicMock(), response=resp)
    assert _is_retryable(exc) is True


def test_is_retryable_4xx_not_429():
    """400 is not retryable."""
    resp = httpx.Response(400, text="Bad Request")
    exc = httpx.HTTPStatusError("400", request=MagicMock(), response=resp)
    assert _is_retryable(exc) is False
