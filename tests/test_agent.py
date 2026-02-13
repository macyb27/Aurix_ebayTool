"""
Tests für den AURIX Agent
"""

import tempfile
from pathlib import Path

import pytest

from aurix_agent.models import (
    FullAIResult,
    MarketResult,
    PricingResult,
    VisionResult,
)
from aurix_agent.orchestrator import ListingOrchestrator
from aurix_agent.services import (
    ListingService,
    MarketService,
    PricingService,
    VisionService,
)


def _create_dummy_image(path: Path, size: int = 100) -> None:
    """Erstellt ein minimales gültiges JPEG."""
    path.write_bytes(b"\xff\xd8\xff" + b"\x00" * (size - 3) + b"\xff\xd9")


class TestVisionService:
    def test_fallback_without_api_key(self):
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(b"\xff\xd8\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' \",#\x1c\x1c(7),01444\x1f\'9=82<.\xff\xd9")
            path = f.name
        try:
            svc = VisionService()
            result = svc.analyze([path])
            assert result.confidence == 0.0
        finally:
            Path(path).unlink(missing_ok=True)

    def test_invalid_image_count(self):
        svc = VisionService()
        result = svc.analyze([])
        assert result.confidence == 0.0


class TestMarketService:
    def test_simulate_sandbox(self):
        svc = MarketService(use_sandbox=True)
        result = svc.analyze("iPhone 12")
        assert result.median_price > 0
        assert result.q1 <= result.median_price <= result.q3
        assert 0 <= result.demand_score <= 100


class TestPricingService:
    def test_fixed_strategy_low_demand(self):
        market = MarketResult(median_price=100, q1=80, q3=120, demand_score=30)
        vision = VisionResult(confidence=0.8, condition="Gebraucht - Gut")
        svc = PricingService()
        result = svc.analyze(market, vision)
        assert result.strategy == "fixed"
        assert result.fixed_price > 0
        assert result.start_price == 0.0

    def test_auction_strategy_high_demand(self):
        market = MarketResult(median_price=100, q1=80, q3=120, demand_score=70)
        vision = VisionResult(confidence=0.8, condition="Gebraucht - Gut")
        svc = PricingService()
        result = svc.analyze(market, vision)
        assert result.strategy == "auction"
        assert result.start_price > 0


class TestListingService:
    def test_generate(self):
        vision = VisionResult(
            product_name="iPhone 12",
            brand="Apple",
            model="A2172",
            category="Handys",
            condition="Gebraucht - Sehr gut",
            confidence=0.9,
        )
        market = MarketResult(median_price=350, q1=300, q3=400, demand_score=60)
        pricing = PricingResult(
            strategy="fixed",
            fixed_price=320,
            expected_price=320,
        )
        svc = ListingService()
        result = svc.generate(vision, market, pricing)
        assert "iPhone" in result.title
        assert "Apple" in result.title
        assert result.description_html
        assert "Marke" in result.item_specifics or "Apple" in result.title


class TestOrchestrator:
    def test_full_analysis_sandbox(self):
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(b"\xff\xd8\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' \",#\x1c\x1c(7),01444\x1f\'9=82<.\xff\xd9")
            path = f.name
        try:
            orch = ListingOrchestrator(use_ebay_sandbox=True)
            result = orch.analyze([path], market_query="Test Produkt")
            assert isinstance(result, FullAIResult)
            assert result.vision
            assert result.market
            assert result.pricing
            assert result.listing
            json_str = result.model_dump_json()
            assert "vision" in json_str
            assert "market" in json_str
            assert "pricing" in json_str
            assert "listing" in json_str
        finally:
            Path(path).unlink(missing_ok=True)
