"""Listings API Endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user_id
from app.database import get_db
from app.schemas.listing import ListingCreate, ListingResponse, ListingUpdate
from app.services.listing_service import ListingService

router = APIRouter()


@router.post("/", response_model=ListingResponse)
async def create_listing(
    data: ListingCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Listing erstellen (Draft)."""
    service = ListingService(db)
    listing = await service.create_listing(
        title=data.title,
        description=data.description,
        price=float(data.price),
        quantity=data.quantity,
        category_id=data.category_id,
        product_id=data.product_id,
        user_id=data.user_id or user_id,
    )
    return listing


@router.get("/", response_model=list[ListingResponse])
async def list_listings(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Listings des Users abrufen."""
    service = ListingService(db)
    listings = await service.get_user_listings(user_id=user_id)
    return listings


@router.get("/{listing_id}", response_model=ListingResponse)
async def get_listing(
    listing_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Einzelnes Listing abrufen."""
    service = ListingService(db)
    listing = await service.get_listing(listing_id, user_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing nicht gefunden")
    return listing


@router.post("/{listing_id}/publish")
async def publish_listing(
    listing_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Listing bei eBay publizieren (synchron)."""
    from app.tasks.listing_tasks import create_listing_task

    service = ListingService(db)
    listing = await service.get_listing(listing_id, user_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing nicht gefunden")
    create_listing_task.delay(listing_id, user_id)
    return {"status": "queued", "listing_id": listing_id}


@router.patch("/{listing_id}", response_model=ListingResponse)
async def update_listing(
    listing_id: int,
    data: ListingUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Listing aktualisieren."""
    from sqlalchemy import select
    from app.models.listing import Listing

    result = await db.execute(
        select(Listing).where(Listing.id == listing_id, Listing.user_id == user_id)
    )
    listing = result.scalar_one_or_none()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing nicht gefunden")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(listing, key, value)
    await db.flush()
    await db.refresh(listing)
    return listing
