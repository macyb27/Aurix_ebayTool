"""Pydantic Models für AI-Analyse-Ergebnisse – strikt validierbar."""

from decimal import Decimal
from typing import Literal, Optional, Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _coerce_decimal(v: Any) -> Decimal:
    """Coerce int/float zu Decimal."""
    if isinstance(v, Decimal):
        return v
    return Decimal(str(v))


class VisionResult(BaseModel):
    """Ergebnis der Vision/Bildanalyse."""

    model_config = ConfigDict(extra="forbid", strict=True)

    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=5000)
    category_hint: Optional[str] = Field(None, max_length=100)
    condition: Optional[str] = Field(None, max_length=50)
    estimated_price: Optional[Decimal] = Field(None, ge=0)
    brand: Optional[str] = Field(None, max_length=200)
    confidence: float = Field(..., ge=0, le=1, description="Konfidenz 0–1")


class MarketResult(BaseModel):
    """Ergebnis der Marktanalyse."""

    model_config = ConfigDict(extra="forbid", strict=True)

    category_id: str = Field(..., min_length=1, max_length=100)
    search_term: Optional[str] = Field(None, max_length=500)
    avg_sold_price: Optional[Decimal] = Field(None, ge=0)
    sold_count: Optional[int] = Field(None, ge=0)
    active_listings: Optional[int] = Field(None, ge=0)
    demand_score: Optional[float] = Field(None, ge=0, le=100, description="0–100")
    confidence: float = Field(..., ge=0, le=1, description="Konfidenz 0–1")


class PricingResult(BaseModel):
    """Ergebnis der Preiskalkulation."""

    model_config = ConfigDict(extra="forbid", strict=True)

    avg_price: Decimal = Field(..., ge=0)
    min_price: Decimal = Field(..., ge=0)
    max_price: Decimal = Field(..., ge=0)
    recommended_price: Decimal = Field(..., ge=0)
    sample_count: int = Field(..., ge=0)
    confidence: float = Field(..., ge=0, le=1, description="Konfidenz 0–1")

    @field_validator("avg_price", "min_price", "max_price", "recommended_price", mode="before")
    @classmethod
    def coerce_decimal(cls, v: Any) -> Decimal:
        return _coerce_decimal(v)


ListingStrategy = Literal["auction", "fixed"]


class ListingResult(BaseModel):
    """Ergebnis der Listing-Empfehlung."""

    model_config = ConfigDict(extra="forbid", strict=True)

    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=5000)
    price: Decimal = Field(..., ge=0)
    category_id: Optional[str] = Field(None, max_length=100)
    strategy: ListingStrategy = Field(
        ...,
        description="Nur 'auction' oder 'fixed'",
    )
    duration: Optional[str] = Field(None, max_length=20)
    confidence: float = Field(..., ge=0, le=1, description="Konfidenz 0–1")

    @field_validator("price", mode="before")
    @classmethod
    def coerce_price(cls, v: Any) -> Decimal:
        return _coerce_decimal(v)


class FullAIResult(BaseModel):
    """Kombiniertes Ergebnis aller AI-Analysen."""

    model_config = ConfigDict(extra="forbid", strict=True)

    vision: VisionResult
    market: MarketResult
    pricing: PricingResult
    listing: ListingResult
