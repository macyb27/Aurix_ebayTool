"""
FullAIResult Schema - strikt validierbar, nur JSON
"""

from pydantic import BaseModel, Field


class VisionResult(BaseModel):
    product_name: str = ""
    brand: str = ""
    model: str = ""
    category: str = ""
    condition: str = ""
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)


class MarketResult(BaseModel):
    median_price: float = 0.0
    q1: float = 0.0
    q3: float = 0.0
    demand_score: int = Field(ge=0, le=100, default=0)


class PricingResult(BaseModel):
    strategy: str = Field(..., pattern="^(auction|fixed)$")
    start_price: float = 0.0
    fixed_price: float = 0.0
    expected_price: float = 0.0


class ListingResult(BaseModel):
    title: str = ""
    subtitle: str = ""
    description_html: str = ""
    item_specifics: dict[str, str] = Field(default_factory=dict)


class FullAIResult(BaseModel):
    vision: VisionResult
    market: MarketResult
    pricing: PricingResult
    listing: ListingResult
    warnings: list[str] = Field(default_factory=list)


ListingAnalysisResult = FullAIResult
