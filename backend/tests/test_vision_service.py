"""Unit tests for VisionService."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.vision_service import VisionService


@pytest.mark.asyncio
async def test_analyze_images_returns_mock_when_no_api_key(mock_db_session):
    """Analyze images returns mock response when AI not configured."""
    service = VisionService(mock_db_session)
    tenant_id = uuid.uuid4()
    images = ["https://example.com/image1.jpg"]

    result = await service.analyze_images(
        tenant_id=tenant_id,
        images=images,
        product_name="Test Product",
    )

    assert "suggestedCategory" in result
    assert "tags" in result
    assert "attributes" in result
    assert "product" in result["tags"] or "Test Product" in result["tags"]


@pytest.mark.asyncio
async def test_generate_description_returns_mock_when_no_api_key(mock_db_session):
    """Generate description returns mock when AI not configured."""
    service = VisionService(mock_db_session)
    tenant_id = uuid.uuid4()

    result = await service.generate_description(
        tenant_id=tenant_id,
        product_name="Blue Widget",
        product_attributes={"color": "blue", "size": "M"},
        images=[],
    )

    assert "title" in result
    assert "description" in result
    assert "suggestedCategory" in result
    assert "tags" in result
    assert "Blue Widget" in result["title"]


@pytest.mark.asyncio
async def test_get_job_returns_none_when_not_found(mock_db_session):
    """Get job returns None when job does not exist."""
    from sqlalchemy import select
    from app.models.ai import AIJob

    mock_db_session.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None)))
    service = VisionService(mock_db_session)

    result = await service.get_job(uuid.uuid4(), uuid.uuid4())

    assert result is None
