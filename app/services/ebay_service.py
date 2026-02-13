"""eBay API Service - Katalog, Suche, Listing-API."""

import logging
from typing import Any

from app.core.ebay_client import EbayApiClient
from app.core.exceptions import EbayApiError

logger = logging.getLogger(__name__)


class EbayService:
    """Service für eBay API Interaktionen."""

    def __init__(self, client: EbayApiClient | None = None):
        self._client = client or EbayApiClient()

    async def search_listings(
        self,
        query: str,
        *,
        category_ids: str | None = None,
        limit: int = 20,
        token: str | None = None,
    ) -> dict[str, Any]:
        """Suche nach Listings (Browse API)."""
        params: dict[str, Any] = {
            "q": query,
            "limit": str(limit),
        }
        if category_ids:
            params["category_ids"] = category_ids

        return await self._client.get(
            "/buy/browse/v1/item_summary/search",
            params=params,
            token=token,
        )

    async def get_item(self, item_id: str, token: str | None = None) -> dict[str, Any]:
        """Einzelnes Item abrufen."""
        return await self._client.get(
            f"/buy/browse/v1/item/{item_id}",
            token=token,
        )

    async def get_category(self, category_id: str, token: str | None = None) -> dict[str, Any]:
        """Kategorie-Details abrufen."""
        return await self._client.get(
            f"/buy/browse/v1/category/{category_id}",
            token=token,
        )

    async def get_category_tree(self, token: str | None = None) -> dict[str, Any]:
        """Kategorie-Baum abrufen."""
        return await self._client.get(
            "/buy/browse/v1/category_tree/0",
            token=token,
        )

    async def create_inventory_item(
        self,
        sku: str,
        payload: dict[str, Any],
        token: str | None = None,
    ) -> dict[str, Any]:
        """Inventory Item erstellen (Inventory API)."""
        return await self._client.put(
            f"/sell/inventory/v1/inventory_item/{sku}",
            json=payload,
            token=token,
        )

    async def create_offer(
        self,
        payload: dict[str, Any],
        token: str | None = None,
    ) -> dict[str, Any]:
        """Offer erstellen (Listing API)."""
        return await self._client.post(
            "/sell/inventory/v1/offer",
            json=payload,
            token=token,
        )

    async def publish_offer(self, offer_id: str, token: str | None = None) -> dict[str, Any]:
        """Offer publizieren."""
        return await self._client.post(
            f"/sell/inventory/v1/offer/{offer_id}/publish",
            token=token,
        )
