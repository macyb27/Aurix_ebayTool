"""Pricing schemas."""

from pydantic import BaseModel


class PriceSuggestionRequest(BaseModel):
    """Price suggestion request."""

    basePrice: float
    categoryId: str | None = None
    condition: str | None = None


class PriceSuggestionResponse(BaseModel):
    """Price suggestion response."""

    suggestedPrice: float
    minPrice: float
    maxPrice: float
    confidence: float
    factors: dict
