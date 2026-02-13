"""Tests für AI API: JSON Validation, Mock Response, Integration, Failure."""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.database import get_db
from app.core.exceptions import ValidationError
from app.services.ai_integration_service import AIIntegrationService


# --- Unit Tests: JSON Validation ---


@pytest.mark.asyncio
async def test_json_validation_valid_full_structure(db_session):
    """Gültiges FullAIResult-JSON mit allen Feldern."""
    service = AIIntegrationService(db_session)
    raw = """
    {
      "vision": {
        "title": "MacBook Pro",
        "description": "Laptop",
        "category_hint": "9355",
        "condition": "Neu",
        "estimated_price": 1200,
        "brand": "Apple",
        "confidence": 0.95
      },
      "market": {
        "category_id": "9355",
        "search_term": "laptop",
        "avg_sold_price": 1100,
        "sold_count": 150,
        "active_listings": 80,
        "demand_score": 85.5,
        "confidence": 0.88
      },
      "pricing": {
        "avg_price": 1100,
        "min_price": 800,
        "max_price": 1500,
        "recommended_price": 1045,
        "sample_count": 100,
        "confidence": 0.9
      },
      "listing": {
        "title": "MacBook Pro",
        "description": "Top Zustand",
        "price": 1045,
        "category_id": "9355",
        "strategy": "auction",
        "duration": "GTC",
        "confidence": 0.92
      }
    }
    """
    result = service._validate_json(raw)
    assert result.vision.title == "MacBook Pro"
    assert result.vision.confidence == 0.95
    assert result.market.demand_score == 85.5
    assert result.listing.strategy == "auction"


@pytest.mark.asyncio
async def test_json_validation_confidence_bounds(db_session):
    """Confidence außerhalb 0–1 wirft ValidationError."""
    service = AIIntegrationService(db_session)
    raw = """
    {
      "vision": {"title": "x", "confidence": 1.5},
      "market": {"category_id": "x", "confidence": 0.5},
      "pricing": {"avg_price": 1, "min_price": 1, "max_price": 1, "recommended_price": 1, "sample_count": 1, "confidence": 0.5},
      "listing": {"title": "x", "price": 1, "strategy": "fixed", "confidence": 0.5}
    }
    """
    with pytest.raises(ValidationError):
        service._validate_json(raw)


@pytest.mark.asyncio
async def test_json_validation_demand_score_bounds(db_session):
    """demand_score > 100 wirft ValidationError."""
    service = AIIntegrationService(db_session)
    raw = """
    {
      "vision": {"title": "x", "confidence": 0.5},
      "market": {"category_id": "x", "demand_score": 150, "confidence": 0.5},
      "pricing": {"avg_price": 1, "min_price": 1, "max_price": 1, "recommended_price": 1, "sample_count": 1, "confidence": 0.5},
      "listing": {"title": "x", "price": 1, "strategy": "fixed", "confidence": 0.5}
    }
    """
    with pytest.raises(ValidationError):
        service._validate_json(raw)


@pytest.mark.asyncio
async def test_json_validation_markdown_codeblock(db_session):
    """JSON in Markdown-Codeblock wird extrahiert."""
    service = AIIntegrationService(db_session)
    raw = '''```json
    {"vision": {"title": "InBlock", "confidence": 0.5},
     "market": {"category_id": "x", "confidence": 0.5},
     "pricing": {"avg_price": 1, "min_price": 1, "max_price": 1, "recommended_price": 1, "sample_count": 1, "confidence": 0.5},
     "listing": {"title": "x", "price": 1, "strategy": "fixed", "confidence": 0.5}}
    ```'''
    result = service._validate_json(raw)
    assert result.vision.title == "InBlock"


@pytest.mark.asyncio
async def test_json_validation_empty_string_raises(db_session):
    """Leerer String wirft ValidationError."""
    service = AIIntegrationService(db_session)
    with pytest.raises(ValidationError):
        service._validate_json("")


# --- Mock AI Response Test ---


@pytest.mark.asyncio
async def test_mock_ai_response_full_flow(db_session):
    """Mock LLM liefert gültiges FullAIResult – komplette Pipeline."""
    valid_json = """
    {
      "vision": {"title": "iPhone 15", "confidence": 0.92},
      "market": {"category_id": "9355", "demand_score": 78, "confidence": 0.85},
      "pricing": {"avg_price": 850, "min_price": 700, "max_price": 999, "recommended_price": 807, "sample_count": 45, "confidence": 0.88},
      "listing": {"title": "iPhone 15", "price": 807, "strategy": "fixed", "confidence": 0.9}
    }
    """
    with patch("openai.AsyncOpenAI") as mock_openai:
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message.content = valid_json
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai.return_value = mock_client

        service = AIIntegrationService(db_session, api_key="test-key")
        result = await service.analyze("Analysiere iPhone 15 für eBay", user_id="u1")

        assert result.vision.title == "iPhone 15"
        assert result.pricing.recommended_price == 807
        assert result.listing.strategy == "fixed"
        mock_client.chat.completions.create.assert_called_once()
    await db_session.rollback()


# --- Integration Test: /api/v1/ai/analyze ---


@pytest_asyncio.fixture
async def client_with_db(db_session):
    """FastAPI Client mit DB-Override."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_api_ai_analyze_success(client_with_db):
    """POST /api/v1/ai/analyze liefert FullAIResult bei gültiger Mock-Response."""
    valid_json = """
    {
      "vision": {"title": "Test Produkt", "confidence": 0.9},
      "market": {"category_id": "9355", "confidence": 0.8},
      "pricing": {"avg_price": 100, "min_price": 80, "max_price": 120, "recommended_price": 95, "sample_count": 50, "confidence": 0.85},
      "listing": {"title": "Test Produkt", "price": 95, "strategy": "fixed", "confidence": 0.9}
    }
    """
    with patch("openai.AsyncOpenAI") as mock_openai, patch(
        "app.services.ai_integration_service.get_settings"
    ) as mock_settings:
        mock_settings.return_value.openai_api_key = "test-key"
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message.content = valid_json
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai.return_value = mock_client

        response = await client_with_db.post(
            "/api/v1/ai/analyze",
            json={"prompt": "Analysiere Laptop"},
        )

        assert response.status_code == 200, response.text
        data = response.json()
        assert "vision" in data
        assert data["vision"]["title"] == "Test Produkt"
        assert data["listing"]["strategy"] == "fixed"


# --- Failure Test: Invalid JSON ---


@pytest.mark.asyncio
async def test_api_ai_analyze_failure_invalid_json(client_with_db):
    """POST /api/v1/ai/analyze liefert 422 wenn LLM ungültiges JSON zurückgibt."""
    invalid_json = "not valid json at all {{{"
    with patch("openai.AsyncOpenAI") as mock_openai, patch(
        "app.services.ai_integration_service.get_settings"
    ) as mock_settings:
        mock_settings.return_value.openai_api_key = "test-key"
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message.content = invalid_json
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai.return_value = mock_client

        response = await client_with_db.post(
            "/api/v1/ai/analyze",
            json={"prompt": "test"},
        )

        assert response.status_code == 422
        assert response.json().get("type") == "validation_error"


@pytest.mark.asyncio
async def test_api_ai_analyze_failure_invalid_structure(client_with_db):
    """POST /api/v1/ai/analyze liefert 422 bei falscher JSON-Struktur."""
    wrong_structure = '{"vision": {}, "market": {}, "other": "stuff"}'
    with patch("openai.AsyncOpenAI") as mock_openai, patch(
        "app.services.ai_integration_service.get_settings"
    ) as mock_settings:
        mock_settings.return_value.openai_api_key = "test-key"
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message.content = wrong_structure
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai.return_value = mock_client

        response = await client_with_db.post(
            "/api/v1/ai/analyze",
            json={"prompt": "test"},
        )

        assert response.status_code == 422
        assert "validation" in response.json().get("detail", "").lower() or "validation_error" in str(response.json())
