"""
ListingOrchestrator - Führt alle Services zusammen und liefert einheitliches JSON
"""

import logging
from pathlib import Path
from typing import Any

from aurix_agent.models import (
    FullAIResult,
    MarketResult,
    PricingResult,
    VisionResult,
)
from aurix_agent.services import (
    ListingService,
    MarketService,
    PricingService,
    VisionService,
)

logger = logging.getLogger(__name__)


class ListingOrchestrator:
    """
    Orchestriert Vision, Market, Pricing und Listing Services.
    Gibt ein einheitliches JSON zurück.
    """

    def __init__(
        self,
        openai_api_key: str | None = None,
        use_ebay_sandbox: bool = True,
    ):
        self.vision = VisionService(api_key=openai_api_key)
        self.market = MarketService(use_sandbox=use_ebay_sandbox)
        self.pricing = PricingService()
        self.listing = ListingService()

    def analyze(
        self,
        image_paths: list[str | Path],
        openai_api_key: str | None = None,
        market_query: str | None = None,
    ) -> FullAIResult:
        """
        Führt vollständige Listing-Analyse durch.

        Args:
            image_paths: 1-3 Pfade zu Produktbildern
            openai_api_key: Optionaler OpenAI API-Key
            market_query: Optionaler Suchbegriff für Marktanalyse (sonst aus Vision)

        Returns:
            FullAIResult mit vision, market, pricing, listing
        """
        # 1. Vision
        vision = self.vision.analyze(
            image_paths=image_paths,
            api_key=openai_api_key,
        )

        # 2. Market
        query = market_query or vision.product_name or "Produkt"
        market = self.market.analyze(
            query=query,
            category=vision.category,
            vision=vision,
        )

        # 3. Pricing
        pricing = self.pricing.analyze(market=market, vision=vision)

        listing = self.listing.generate(
            vision=vision,
            market=market,
            pricing=pricing,
        )

        return FullAIResult(
            vision=vision,
            market=market,
            pricing=pricing,
            listing=listing,
        )

    def analyze_to_json(
        self,
        image_paths: list[str | Path],
        **kwargs: Any,
    ) -> str:
        """
        Wie analyze(), gibt aber JSON-String zurück.
        """
        result = self.analyze(image_paths=image_paths, **kwargs)
        return result.model_dump_json(indent=2)


def run_analysis(
    image_paths: list[str | Path],
    openai_api_key: str | None = None,
    market_query: str | None = None,
    use_ebay_sandbox: bool = True,
) -> str:
    """
    Convenience-Funktion: Führt Analyse durch und gibt JSON zurück.

    Args:
        image_paths: 1-3 Bildpfade
        openai_api_key: Optional
        market_query: Optional
        use_ebay_sandbox: eBay Sandbox nutzen

    Returns:
        JSON-String mit vision, market, pricing, listing
    """
    orch = ListingOrchestrator(
        openai_api_key=openai_api_key,
        use_ebay_sandbox=use_ebay_sandbox,
    )
    return orch.analyze_to_json(
        image_paths=image_paths,
        openai_api_key=openai_api_key,
        market_query=market_query,
    )
