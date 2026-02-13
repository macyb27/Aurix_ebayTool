"""PricingService - Price suggestions and pricing logic."""

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class PricingService:
    """Pricing logic and suggestions."""

    def __init__(self):
        pass

    def suggest_price(
        self,
        base_price: float,
        category_id: Optional[str] = None,
        condition: Optional[str] = None,
        market_data: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Suggest listing price based on base price and optional market data.
        Returns min, max, suggested price and confidence.
        """
        # Simplified: no external market data integration yet
        margin_low = 0.95
        margin_high = 1.15
        if condition == "used":
            margin_low = 0.6
            margin_high = 0.9
        elif condition == "refurbished":
            margin_low = 0.7
            margin_high = 0.95

        min_price = round(base_price * margin_low, 2)
        max_price = round(base_price * margin_high, 2)
        suggested = round(base_price * (margin_low + margin_high) / 2, 2)

        return {
            "suggestedPrice": suggested,
            "minPrice": min_price,
            "maxPrice": max_price,
            "confidence": 0.7,
            "factors": {
                "basePrice": base_price,
                "condition": condition or "new",
                "categoryId": category_id,
            },
        }

    def calculate_shipping_cost(
        self,
        weight_kg: Optional[float] = None,
        dimensions: Optional[dict[str, float]] = None,
        destination_country: str = "DE",
    ) -> float:
        """Calculate estimated shipping cost (simplified)."""
        base_cost = 4.99
        if weight_kg and weight_kg > 2:
            base_cost += (weight_kg - 2) * 1.5
        return round(base_cost, 2)

    def validate_price(self, price: float, min_allowed: float = 0.01) -> bool:
        """Validate price is within allowed range."""
        return price >= min_allowed and price < 1_000_000
