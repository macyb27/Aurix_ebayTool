"""
Pydantic-Modelle für alle Service-Outputs
"""

from typing import Any
from pydantic import BaseModel, Field


class VisionResult(BaseModel):
    """VisionService Output"""
    product_name: str = ""
    brand: str = ""
    model: str = ""
    category: str = ""
    condition: str = ""
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    warnings: list[str] = Field(default_factory=list)


class MarketResult(BaseModel):
    """MarketService Output"""
    median_price: float = 0.0
    q1: float = 0.0
    q3: float = 0.0
    demand_score: int = Field(ge=0, le=100, default=0)
    sample_count: int = 0
    warnings: list[str] = Field(default_factory=list)


class PricingResult(BaseModel):
    """PricingService Output"""
    strategy: str = Field(..., pattern="^(auction|fixed)$")
    start_price: float = 0.0
    fixed_price: float = 0.0
    expected_price: float = 0.0
    reasoning: str = ""
    warnings: list[str] = Field(default_factory=list)


class ListingResult(BaseModel):
    """ListingService Output"""
    title: str = ""
    subtitle: str = ""
    description_html: str = ""
    item_specifics: dict[str, str] = Field(default_factory=dict)
    keywords: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ListingAnalysisResult(BaseModel):
    """Einheitliches Gesamt-Output aller Services"""
    vision: VisionResult
    market: MarketResult
    pricing: PricingResult
    listing: ListingResult
    meta: dict[str, Any] = Field(default_factory=dict)
