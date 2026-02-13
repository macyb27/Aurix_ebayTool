"""Pytest fixtures."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
def tenant_id() -> uuid.UUID:
    """Sample tenant ID."""
    return uuid.uuid4()


@pytest.fixture
def product_id() -> uuid.UUID:
    """Sample product ID."""
    return uuid.uuid4()


@pytest.fixture
def listing_id() -> uuid.UUID:
    """Sample listing ID."""
    return uuid.uuid4()


@pytest.fixture
def mock_db_session():
    """Mock async database session."""
    return AsyncMock(spec=AsyncSession)
