"""API dependencies."""

from uuid import UUID

from fastapi import Header, HTTPException, status

from app.core.database import DbSession
from app.services.ebay_client import EbayClient
from app.services.ebay_service import EbayService
from app.services.listing_service import ListingService
from app.services.market_service import MarketService
from app.services.pricing_service import PricingService
from app.services.vision_service import VisionService


async def get_tenant_id(
    x_tenant_id: str | None = Header(None, alias="X-Tenant-Id"),
) -> UUID:
    """Extract tenant ID from header (required for multi-tenant)."""
    if not x_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Tenant-Id header is required",
        )
    try:
        return UUID(x_tenant_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tenant ID format",
        )


def get_listing_service(db: DbSession) -> ListingService:
    """Get ListingService."""
    return ListingService(db)


def get_vision_service(db: DbSession) -> VisionService:
    """Get VisionService."""
    return VisionService(db)


def get_market_service(db: DbSession) -> MarketService:
    """Get MarketService."""
    return MarketService(db)


def get_pricing_service() -> PricingService:
    """Get PricingService."""
    return PricingService()


def get_ebay_service(db: DbSession) -> EbayService:
    """Get EbayService."""
    return EbayService(db)
