"""eBay API client with retry, token handling, and error handling."""

import logging
from typing import Any, Optional

import httpx
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
    wait_fixed,
)

from app.core.config import get_settings
from app.core.exceptions import EbayApiError, EbayRateLimitError

logger = logging.getLogger(__name__)
settings = get_settings()


def _is_retryable(exc: BaseException) -> bool:
    """Check if exception is retryable."""
    if isinstance(exc, EbayRateLimitError):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in (429, 500, 502, 503, 504)
    if isinstance(exc, (httpx.ConnectError, httpx.TimeoutException)):
        return True
    return False


def _get_wait_strategy(exc: BaseException):
    """Custom wait for rate limit vs exponential for others."""
    if isinstance(exc, EbayRateLimitError):
        return wait_fixed(getattr(exc, "retry_after", 60))
    return wait_exponential(multiplier=1, min=1, max=60)


class EbayClient:
    """eBay API client with retry and token refresh."""

    def __init__(
        self,
        app_id: Optional[str] = None,
        cert_id: Optional[str] = None,
        sandbox: Optional[bool] = None,
        base_url: Optional[str] = None,
    ):
        self.app_id = app_id or settings.ebay_app_id
        self.cert_id = cert_id or settings.ebay_cert_id
        self.sandbox = sandbox if sandbox is not None else settings.ebay_sandbox
        self._base_url = base_url or settings.ebay_api_base_url
        self._access_token: Optional[str] = None

    @retry(
        retry=retry_if_exception(_is_retryable),
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=60),
        reraise=True,
    )
    async def _request(
        self,
        method: str,
        path: str,
        *,
        token: Optional[str] = None,
        json: Optional[dict] = None,
        params: Optional[dict] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make HTTP request with retry."""
        url = f"{self._base_url.rstrip('/')}/{path.lstrip('/')}"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {token or self._access_token}",
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method, url, headers=headers, json=json, params=params, **kwargs
            )
            await self._handle_response(response)
            return response

    async def _handle_response(self, response: httpx.Response) -> None:
        """Handle response and raise appropriate errors."""
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            raise EbayRateLimitError(retry_after=retry_after)
        if response.status_code >= 400:
            try:
                error_data = response.json()
                message = error_data.get("errors", [{}])[0].get("message", response.text)
                error_id = error_data.get("errors", [{}])[0].get("errorId", "")
            except Exception:
                message = response.text
                error_id = ""
            raise EbayApiError(
                message=message,
                status_code=response.status_code,
                ebay_error_code=error_id if error_id else None,
            )

    def set_access_token(self, token: str) -> None:
        """Set OAuth access token."""
        self._access_token = token

    async def get_access_token(self, refresh_token: str) -> str:
        """Refresh OAuth token using refresh token."""
        url = settings.ebay_oauth_url
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.app_id,
            "client_secret": self.cert_id,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data)
            if response.status_code != 200:
                raise EbayApiError(
                    message=f"Token refresh failed: {response.text}",
                    status_code=response.status_code,
                )
            result = response.json()
            self._access_token = result["access_token"]
            return result["access_token"]

    async def get_item(self, item_id: str, token: Optional[str] = None) -> dict:
        """Get item from eBay."""
        response = await self._request(
            "GET",
            f"/sell/inventory/v1/inventory_item/{item_id}",
            token=token,
        )
        return response.json()

    async def create_or_replace_inventory(
        self, sku: str, payload: dict, token: Optional[str] = None
    ) -> None:
        """Create or replace inventory item."""
        await self._request(
            "PUT",
            f"/sell/inventory/v1/inventory_item/{sku}",
            json=payload,
            token=token,
        )

    async def create_offer(self, payload: dict, token: Optional[str] = None) -> dict:
        """Create offer."""
        response = await self._request(
            "POST",
            "/sell/inventory/v1/offer",
            json=payload,
            token=token,
        )
        return response.json()

    async def publish_offer(self, offer_id: str, token: Optional[str] = None) -> dict:
        """Publish offer to eBay."""
        response = await self._request(
            "POST",
            f"/sell/inventory/v1/offer/{offer_id}/publish",
            token=token,
        )
        return response.json()

    async def get_categories(self, marketplace_id: str = "EBAY_DE") -> dict:
        """Get category tree (public API, no auth required for some endpoints)."""
        response = await self._request(
            "GET",
            f"/commerce/taxonomy/v1/category_tree/{marketplace_id}",
        )
        return response.json()
