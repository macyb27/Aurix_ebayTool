"""Unit tests for PricingService."""

import pytest

from app.services.pricing_service import PricingService


def test_suggest_price_returns_valid_structure():
    """Price suggestion returns valid structure."""
    service = PricingService()
    result = service.suggest_price(base_price=29.99, condition="new")

    assert "suggestedPrice" in result
    assert "minPrice" in result
    assert "maxPrice" in result
    assert "confidence" in result
    assert result["suggestedPrice"] >= result["minPrice"]
    assert result["suggestedPrice"] <= result["maxPrice"]


def test_suggest_price_used_condition_lower_margins():
    """Used condition has lower price margins."""
    service = PricingService()

    new_result = service.suggest_price(base_price=100, condition="new")
    used_result = service.suggest_price(base_price=100, condition="used")

    assert used_result["maxPrice"] < new_result["maxPrice"]
    assert used_result["suggestedPrice"] < new_result["suggestedPrice"]


def test_validate_price_accepts_valid():
    """Validate price accepts valid prices."""
    service = PricingService()
    assert service.validate_price(10.99) is True
    assert service.validate_price(0.01) is True


def test_validate_price_rejects_invalid():
    """Validate price rejects invalid prices."""
    service = PricingService()
    assert service.validate_price(0) is False
    assert service.validate_price(-1) is False


def test_calculate_shipping_cost():
    """Calculate shipping cost returns positive value."""
    service = PricingService()
    cost = service.calculate_shipping_cost(weight_kg=1.0)
    assert cost >= 0
    assert isinstance(cost, float)
