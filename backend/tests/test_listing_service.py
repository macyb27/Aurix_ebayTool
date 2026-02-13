"""Unit tests for ListingService."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.listing import Listing
from app.services.listing_service import ListingService


@pytest.mark.asyncio
async def test_create_listing_creates_draft(mock_db_session, tenant_id, product_id):
    """Create listing creates draft status."""
    mock_db_session.add = MagicMock()
    mock_db_session.flush = AsyncMock()

    service = ListingService(mock_db_session)
    listing = await service.create_listing(
        tenant_id=tenant_id,
        product_id=product_id,
        title="A" * 10,
        description="Test description",
        price=29.99,
        quantity=5,
    )

    assert listing.status == "draft"
    assert listing.workflow_step == "draft"
    assert listing.title == "A" * 10
    assert listing.price == 29.99


@pytest.mark.asyncio
async def test_get_workflow_next_steps_draft():
    """Draft has review and publish as next steps."""
    service = ListingService(MagicMock())
    steps = await service.get_workflow_next_steps("draft")
    assert "review" in steps
    assert "publish" in steps


@pytest.mark.asyncio
async def test_get_workflow_next_steps_approved():
    """Approved has publish as next step."""
    service = ListingService(MagicMock())
    steps = await service.get_workflow_next_steps("approved")
    assert "publish" in steps
