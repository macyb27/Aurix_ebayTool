"""Unit-Tests für AIIntegrationService."""

import pytest
from unittest.mock import AsyncMock, patch

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ValidationError
from app.schemas.ai_results import FullAIResult, VisionResult, MarketResult, PricingResult, ListingResult
from app.services.ai_integration_service import AIIntegrationService


@pytest.mark.asyncio
async def test_validate_json_valid(db_session: AsyncSession):
    """Gültiges JSON wird zu FullAIResult validiert."""
    service = AIIntegrationService(db_session)
    raw = """
    {
      "vision": {"title": "Test", "confidence": 0.9},
      "market": {"category_id": "9355", "confidence": 0.8},
      "pricing": {"avg_price": 100, "min_price": 80, "max_price": 120, "recommended_price": 95, "sample_count": 10, "confidence": 0.85},
      "listing": {"title": "Item", "price": 99, "strategy": "fixed", "confidence": 0.9}
    }
    """
    result = service._validate_json(raw)
    assert isinstance(result, FullAIResult)
    assert result.vision.title == "Test"
    assert result.listing.strategy == "fixed"


@pytest.mark.asyncio
async def test_validate_json_invalid_raises(db_session: AsyncSession):
    """Ungültiges JSON wirft ValidationError."""
    service = AIIntegrationService(db_session)
    with pytest.raises(ValidationError, match="Ungültiges JSON|Validierung"):
        service._validate_json("not json {{{")


@pytest.mark.asyncio
async def test_validate_json_invalid_structure_raises(db_session: AsyncSession):
    """JSON mit falscher Struktur wirft ValidationError."""
    service = AIIntegrationService(db_session)
    with pytest.raises(ValidationError, match="Validierung"):
        service._validate_json('{"vision": {}, "market": {}}')


@pytest.mark.asyncio
async def test_validate_json_invalid_strategy_raises(db_session: AsyncSession):
    """Strategy außer auction/fixed wirft ValidationError."""
    service = AIIntegrationService(db_session)
    raw = """
    {
      "vision": {"title": "x", "confidence": 0.5},
      "market": {"category_id": "x", "confidence": 0.5},
      "pricing": {"avg_price": 1, "min_price": 1, "max_price": 1, "recommended_price": 1, "sample_count": 1, "confidence": 0.5},
      "listing": {"title": "x", "price": 1, "strategy": "invalid", "confidence": 0.5}
    }
    """
    with pytest.raises(ValidationError):
        service._validate_json(raw)


@pytest.mark.asyncio
async def test_save_to_db(db_session: AsyncSession):
    """Ergebnis wird in DB gespeichert."""
    service = AIIntegrationService(db_session)
    result = FullAIResult(
        vision=VisionResult(title="T", confidence=0.5),
        market=MarketResult(category_id="x", confidence=0.5),
        pricing=PricingResult(avg_price=1, min_price=1, max_price=1, recommended_price=1, sample_count=1, confidence=0.5),
        listing=ListingResult(title="T", price=1, strategy="fixed", confidence=0.5),
    )
    record = await service._save_to_db(result, prompt="test", user_id="u1")
    assert record.id is not None
    assert record.user_id == "u1"
    assert record.result_json["vision"]["title"] == "T"
    await db_session.rollback()


@pytest.mark.asyncio
async def test_analyze_missing_api_key_raises(db_session: AsyncSession):
    """Ohne API-Key wirft analyze ValidationError (kein LLM-Aufruf)."""
    service = AIIntegrationService(db_session)
    with pytest.raises(ValidationError, match="API Key"):
        await service.analyze("test prompt")


@pytest.mark.asyncio
async def test_analyze_with_mock_llm(db_session: AsyncSession):
    """Analyze mit gemocktem LLM: Aufruf, Validierung, Speicherung."""
    valid_json = """
    {
      "vision": {"title": "Laptop", "confidence": 0.9},
      "market": {"category_id": "9355", "demand_score": 75, "confidence": 0.8},
      "pricing": {"avg_price": 100, "min_price": 80, "max_price": 120, "recommended_price": 95, "sample_count": 50, "confidence": 0.85},
      "listing": {"title": "Laptop", "price": 95, "strategy": "fixed", "confidence": 0.9}
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
        result = await service.analyze("Analysiere Laptop", user_id="u1")

        assert isinstance(result, FullAIResult)
        assert result.vision.title == "Laptop"
        mock_client.chat.completions.create.assert_called_once()
    await db_session.rollback()


@pytest.mark.asyncio
async def test_call_llm_retry_on_api_failure(db_session: AsyncSession):
    """Retry (max 3) bei API-Fehlern – nach 3 Versuchen wird ConnectionError geworfen."""
    with patch("openai.AsyncOpenAI") as mock_openai:
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(
            side_effect=ConnectionError("API unreachable")
        )

        mock_openai.return_value = mock_client

        service = AIIntegrationService(db_session, api_key="test-key")
        with pytest.raises(ConnectionError, match="API"):
            await service.analyze("test")
        assert mock_client.chat.completions.create.call_count == 3
