"""
MarketService - Marktanalyse via eBay Browse API oder Sandbox
Berechnet Median, Q1, Q3 und Demand Score aus Verkaufsdaten.
"""

import logging
import os
from typing import Any

import requests
from pydantic import ValidationError

from aurix_agent.models import MarketResult, VisionResult

logger = logging.getLogger(__name__)

EBAY_BROWSE_URL = "https://api.ebay.com/buy/browse/v1/item_summary/search"
EBAY_SANDBOX_URL = "https://api.sandbox.ebay.com/buy/browse/v1/item_summary/search"


def _percentile(data: list[float], p: float) -> float:
    """Berechnet Perzentil (q1=0.25, median=0.5, q3=0.75)."""
    if not data:
        return 0.0
    sorted_data = sorted(data)
    n = len(sorted_data)
    k = (n - 1) * p
    f = int(k)
    c = f + 1 if f + 1 < n else f
    return sorted_data[f] + (k - f) * (sorted_data[c] - sorted_data[f]) if c != f else sorted_data[f]


def _demand_score(prices: list[float], median: float) -> int:
    """
    Demand Score 0-100 basierend auf:
    - Verkaufsvolumen (mehr Verkäufe = höherer Score)
    - Preisstreuung (engere Streuung = stabilerer Markt)
    """
    if not prices or median <= 0:
        return 0
    n = len(prices)
    volume_score = min(100, n * 2)  # Bis 50 Verkäufe = 100
    std = (sum((p - median) ** 2 for p in prices) / n) ** 0.5 if n > 1 else 0
    cv = std / median if median else 0
    stability_score = max(0, 100 - int(cv * 100))  # Niedrige Varianz = höher
    return min(100, (volume_score + stability_score) // 2)


class MarketService:
    """Marktanalyse via eBay Browse API oder simulierte Sandbox-Daten."""

    def __init__(self, use_sandbox: bool = True):
        self.use_sandbox = use_sandbox
        self._client_id = os.environ.get("EBAY_CLIENT_ID", "")

    def analyze(
        self,
        query: str,
        category: str = "",
        vision: VisionResult | None = None,
        limit: int = 50,
    ) -> MarketResult:
        """
        Holt Verkaufsdaten und berechnet Marktstatistiken.

        Args:
            query: Suchbegriff (z.B. Produktname)
            category: Optionale eBay-Kategorie
            vision: Optionales VisionResult für bessere Suche
            limit: Max. Anzahl Verkäufe (Standard: 50)

        Returns:
            MarketResult mit median_price, q1, q3, demand_score
        """
        search_query = query or (vision.product_name if vision else "")
        if not search_query:
            return MarketResult()

        if self._client_id:
            return self._fetch_ebay(search_query, category, limit)
        return self._simulate_sandbox(search_query, vision)

    def _fetch_ebay(
        self,
        query: str,
        category: str,
        limit: int,
    ) -> MarketResult:
        """Nutzt eBay Browse API (letzte Verkäufe)."""
        base = EBAY_SANDBOX_URL if self.use_sandbox else EBAY_BROWSE_URL
        headers = {
            "Authorization": f"Bearer {self._get_oauth_token()}",
            "X-EBAY-C-MARKETPLACE-ID": "EBAY_DE",
        }
        params: dict[str, Any] = {
            "q": query,
            "limit": min(limit, 200),
            "filter": "buyingOptions:{FIXED_PRICE}",
        }
        if category:
            params["category_ids"] = category

        try:
            resp = requests.get(base, headers=headers, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            return self._process_ebay_response(data)
        except requests.RequestException as e:
            logger.warning("eBay API Fehler, nutze Sandbox: %s", e)
            return self._simulate_sandbox(query, None)

    def _get_oauth_token(self) -> str:
        """Holt OAuth Token für eBay API. Vereinfacht: Client Credentials."""
        url = "https://api.sandbox.ebay.com/identity/v1/oauth2/token"
        if not self.use_sandbox:
            url = "https://api.ebay.com/identity/v1/oauth2/token"
        client_secret = os.environ.get("EBAY_CLIENT_SECRET", "")
        resp = requests.post(
            url,
            data={"grant_type": "client_credentials", "scope": "https://api.ebay.com/oauth/api_scope"},
            auth=(self._client_id, client_secret),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()["access_token"]

    def _process_ebay_response(self, data: dict) -> MarketResult:
        items = data.get("itemSummaries", [])
        prices = []
        for item in items:
            price = item.get("price", {}).get("value")
            if price is not None:
                prices.append(float(price))
        return self._compute_statistics(prices)

    def _simulate_sandbox(
        self,
        query: str,
        vision: VisionResult | None,
    ) -> MarketResult:
        """Simuliert Marktdaten für Tests ohne API."""
        import random

        base_price = 50.0 + hash(query) % 200
        n = random.randint(15, 50)
        prices = [
            base_price * (0.7 + random.random() * 0.6)
            for _ in range(n)
        ]
        if vision and vision.confidence > 0.5:
            if "phone" in vision.category.lower() or "handy" in vision.category.lower():
                base_price = 200.0 + hash(query) % 400
                prices = [base_price * (0.8 + random.random() * 0.4) for _ in range(n)]
        return self._compute_statistics(prices)

    def _compute_statistics(self, prices: list[float]) -> MarketResult:
        if not prices:
            return MarketResult()
        median = _percentile(prices, 0.5)
        q1 = _percentile(prices, 0.25)
        q3 = _percentile(prices, 0.75)
        demand = _demand_score(prices, median)
        try:
            return MarketResult(
                median_price=round(median, 2),
                q1=round(q1, 2),
                q3=round(q3, 2),
                demand_score=demand,
            )
        except ValidationError:
            return MarketResult()
