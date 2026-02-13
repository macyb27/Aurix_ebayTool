"""Unit-Tests für VisionService."""

import pytest
from unittest.mock import AsyncMock, patch

from app.services.vision_service import VisionService
from app.core.exceptions import VisionServiceError


@pytest.mark.asyncio
async def test_analyze_image_requires_input():
    """Ohne URL und Pfad wird Fehler geworfen."""
    service = VisionService()
    with pytest.raises(VisionServiceError, match="image_url oder image_path"):
        await service.analyze_image()


@pytest.mark.asyncio
async def test_analyze_image_mock_without_api_key():
    """Ohne API-Key wird Mock-Analyse zurückgegeben."""
    service = VisionService()
    result = await service.analyze_image(image_url="https://example.com/image.jpg")

    assert "title" in result
    assert "description" in result
    assert "category_hint" in result
    assert "condition" in result
    assert "estimated_price" in result


@pytest.mark.asyncio
async def test_parse_vision_response():
    """Vision-Response wird korrekt geparst."""
    service = VisionService()
    content = '{"title": "Test", "description": "Desc", "category_hint": "123"}'
    result = service._parse_vision_response(content)

    assert result["title"] == "Test"
    assert result["description"] == "Desc"
    assert result["category_hint"] == "123"


@pytest.mark.asyncio
async def test_parse_vision_response_with_codeblock():
    """JSON in Markdown-Codeblock wird extrahiert."""
    service = VisionService()
    content = '```json\n{"title": "InBlock"}\n```'
    result = service._parse_vision_response(content)

    assert result["title"] == "InBlock"


@pytest.mark.asyncio
async def test_mock_analysis():
    """Mock-Analyse liefert erwartete Felder."""
    service = VisionService()
    result = service._mock_analysis()

    assert result["title"] == "Produkt aus Bildanalyse"
    assert result["condition"] == "Gebraucht"
    assert "category_hint" in result
