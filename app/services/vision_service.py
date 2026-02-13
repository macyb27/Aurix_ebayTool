"""Vision Service - Bildanalyse für Produkterkennung."""

import base64
import json
import logging
from pathlib import Path
from typing import Any

import httpx

from app.config import get_settings
from app.core.exceptions import VisionServiceError

logger = logging.getLogger(__name__)


class VisionService:
    """Service für AI-gestützte Bildanalyse (OpenAI Vision)."""

    def __init__(self, api_key: str | None = None):
        self._api_key = api_key or get_settings().openai_api_key

    async def analyze_image(
        self, image_url: str | None = None, image_path: str | None = None
    ) -> dict[str, Any]:
        """Bild analysieren: Produkt, Kategorie, Zustand, geschätzter Preis."""
        if not image_url and not image_path:
            raise VisionServiceError("image_url oder image_path erforderlich")

        if not self._api_key:
            return self._mock_analysis()

        image_content = await self._load_image(image_url, image_path)
        image_data = base64.standard_b64encode(image_content).decode()

        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=self._api_key)
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": (
                                    "Analysiere dieses Produktbild für einen eBay-Listing. "
                                    "Antworte NUR als JSON mit: title, description, "
                                    "category_hint, condition, estimated_price, brand."
                                ),
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                },
                            },
                        ],
                    }
                ],
                max_tokens=500,
            )
            content = response.choices[0].message.content or "{}"
            return self._parse_vision_response(content)
        except Exception as e:
            logger.warning("OpenAI Vision failed, using mock: %s", e)
            return self._mock_analysis()

    async def _load_image(
        self, image_url: str | None, image_path: str | None
    ) -> bytes:
        """Bild laden (URL oder Pfad)."""
        if image_url:
            async with httpx.AsyncClient() as client:
                resp = await client.get(image_url)
                resp.raise_for_status()
                return resp.content
        if image_path:
            return Path(image_path).read_bytes()
        return b""

    def _parse_vision_response(self, content: str) -> dict[str, Any]:
        """Vision-Response parsen."""
        try:
            # JSON aus Markdown-Codeblock extrahieren
            if "```" in content:
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            return json.loads(content.strip())
        except json.JSONDecodeError:
            return {
                "title": content[:200] if content else "Unbekanntes Produkt",
                "description": content or "",
                "category_hint": None,
                "condition": "Gebraucht",
                "estimated_price": None,
                "brand": None,
            }

    def _mock_analysis(self) -> dict[str, Any]:
        """Mock-Analyse wenn kein API-Key."""
        return {
            "title": "Produkt aus Bildanalyse",
            "description": "Bitte Beschreibung ergänzen.",
            "category_hint": "9355",  # eBay Elektronik
            "condition": "Gebraucht",
            "estimated_price": 0.0,
            "brand": None,
        }
