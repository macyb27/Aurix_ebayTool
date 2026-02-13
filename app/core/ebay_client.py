"""eBay API Client mit Token-Handling und Retry."""

import base64
import logging
from datetime import datetime, timezone, timedelta
from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.config import get_settings
from app.core.exceptions import EbayApiError, EbayRateLimitError, EbayTokenError

logger = logging.getLogger(__name__)


class EbayApiClient:
    """eBay API Client mit OAuth Token Handling und Retry."""

    def __init__(
        self,
        app_id: str | None = None,
        cert_id: str | None = None,
        oauth_url: str | None = None,
        api_base_url: str | None = None,
    ):
        settings = get_settings()
        self.app_id = app_id or settings.ebay_app_id
        self.cert_id = cert_id or settings.ebay_cert_id
        self.oauth_url = oauth_url or settings.ebay_oauth_url
        self.api_base_url = (api_base_url or settings.ebay_api_base_url).rstrip("/")
        self._client_token: str | None = None
        self._client_token_expires: datetime | None = None

    def _get_auth_header(self) -> str:
        """Basic Auth für OAuth Token Request."""
        credentials = f"{self.app_id}:{self.cert_id}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"

    async def get_client_token(self) -> str:
        """OAuth Client Credentials Token (App-Level)."""
        if (
            self._client_token
            and self._client_token_expires
            and self._client_token_expires > datetime.now(timezone.utc) + timedelta(minutes=5)
        ):
            return self._client_token

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.oauth_url,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Authorization": self._get_auth_header(),
                },
                data={
                    "grant_type": "client_credentials",
                    "scope": "https://api.ebay.com/oauth/api_scope",
                },
            )

        if response.status_code != 200:
            raise EbayTokenError(
                f"Token request failed: {response.status_code} - {response.text}"
            )

        data = response.json()
        self._client_token = data["access_token"]
        expires_in = data.get("expires_in", 7200)
        self._client_token_expires = datetime.now(timezone.utc) + timedelta(
            seconds=expires_in
        )
        return self._client_token

    def _raise_for_status(self, response: httpx.Response) -> None:
        """Response prüfen und ggf. Exception werfen."""
        if response.status_code == 429:
            raise EbayRateLimitError(
                "eBay Rate Limit exceeded",
                status_code=429,
                response=response.text,
            )
        if response.status_code >= 400:
            raise EbayApiError(
                f"eBay API Error: {response.status_code}",
                status_code=response.status_code,
                response=response.text,
            )

    @retry(
        retry=retry_if_exception_type((EbayRateLimitError, EbayApiError)),
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, min=4, max=60),
        reraise=True,
    )
    async def request(
        self,
        method: str,
        path: str,
        *,
        token: str | None = None,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """HTTP Request an eBay API mit Retry."""
        url = f"{self.api_base_url}{path}"
        auth_token = token or await self.get_client_token()

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=method,
                url=url,
                headers={
                    "Authorization": f"Bearer {auth_token}",
                    "Content-Type": "application/json",
                },
                json=json,
                params=params,
            )

        self._raise_for_status(response)
        return response.json() if response.content else {}

    async def get(self, path: str, **kwargs: Any) -> dict[str, Any]:
        """GET Request."""
        return await self.request("GET", path, **kwargs)

    async def post(self, path: str, **kwargs: Any) -> dict[str, Any]:
        """POST Request."""
        return await self.request("POST", path, **kwargs)

    async def put(self, path: str, **kwargs: Any) -> dict[str, Any]:
        """PUT Request."""
        return await self.request("PUT", path, **kwargs)

    async def delete(self, path: str, **kwargs: Any) -> dict[str, Any]:
        """DELETE Request."""
        return await self.request("DELETE", path, **kwargs)
