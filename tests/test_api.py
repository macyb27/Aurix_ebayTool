"""API Endpoint Tests."""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest_asyncio.fixture
async def api_client():
    """API Test Client ohne DB Override."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_endpoint(api_client: AsyncClient):
    """Health Check liefert 200."""
    response = await api_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_docs_available(api_client: AsyncClient):
    """OpenAPI Docs sind erreichbar."""
    response = await api_client.get("/docs")
    assert response.status_code == 200
