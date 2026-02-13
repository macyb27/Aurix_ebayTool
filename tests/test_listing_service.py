"""Unit-Tests für ListingService."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.listing import Listing, ListingStatus
from app.services.listing_service import ListingService


@pytest.mark.asyncio
async def test_create_listing(db_session: AsyncSession):
    """Listing wird erstellt."""
    service = ListingService(db_session)
    listing = await service.create_listing(
        title="Test Produkt",
        description="Beschreibung",
        price=29.99,
        quantity=1,
        user_id="user-1",
    )

    assert listing.id is not None
    assert listing.title == "Test Produkt"
    assert listing.status == ListingStatus.DRAFT
    assert listing.user_id == "user-1"
    await db_session.rollback()


@pytest.mark.asyncio
async def test_get_listing_not_found(db_session: AsyncSession):
    """Nicht existierendes Listing liefert None."""
    service = ListingService(db_session)
    result = await service.get_listing(99999)
    assert result is None


@pytest.mark.asyncio
async def test_get_user_listings_empty(db_session: AsyncSession):
    """Leere Liste für User ohne Listings."""
    service = ListingService(db_session)
    result = await service.get_user_listings("user-1")
    assert result == []


@pytest.mark.asyncio
async def test_update_status(db_session: AsyncSession):
    """Listing-Status wird aktualisiert."""
    service = ListingService(db_session)
    listing = await service.create_listing(
        title="Test",
        price=10.0,
        user_id="user-1",
    )
    updated = await service.update_status(listing.id, ListingStatus.CANCELLED)
    assert updated is not None
    assert updated.status == ListingStatus.CANCELLED
    await db_session.rollback()
