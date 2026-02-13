"""
VisionService - Bildanalyse via OpenAI Vision API
Analysiert 1-3 Bilder pro Listing und liefert strukturierte Produktdaten.
"""

import base64
import json
import logging
from pathlib import Path
from typing import Union

from openai import OpenAI
from pydantic import ValidationError

from aurix_agent.models import VisionResult

logger = logging.getLogger(__name__)

MIN_CONFIDENCE_THRESHOLD = 0.6

VISION_SYSTEM_PROMPT = """Du bist ein Experte für die Analyse von eBay-Listings. Analysiere die bereitgestellten Produktbilder und extrahiere strukturierte Informationen.

Antworte NUR mit einem gültigen JSON-Objekt in folgendem Format (keine zusätzlichen Erklärungen):
{
  "product_name": "Vollständiger Produktname",
  "brand": "Markenname oder 'Unbekannt'",
  "model": "Modellbezeichnung oder 'Unbekannt'",
  "category": "eBay-Kategorie (z.B. Consumer Electronics > Cell Phones)",
  "condition": "Neu | Gebraucht - Sehr gut | Gebraucht - Gut | Gebraucht - Akzeptabel | Refurbished",
  "confidence": 0.0-1.0
}

Regeln:
- confidence: Schätze deine Zuversicht (0.0-1.0) basierend auf Bildqualität und Erkennbarkeit
- Bei unscharfen oder mehrdeutigen Bildern: confidence < 0.6
- category: Nutze eBay-typische Kategoriebezeichnungen
- condition: Wähle die passendste Option basierend auf sichtbaren Gebrauchsspuren"""


class VisionService:
    """Analysiert Produktbilder via OpenAI Vision API."""

    def __init__(self, api_key: str | None = None):
        self._client = OpenAI(api_key=api_key) if api_key else None

    def analyze(
        self,
        image_paths: list[Union[str, Path]],
        api_key: str | None = None,
    ) -> VisionResult:
        """
        Analysiert 1-3 Bilder und liefert strukturierte Produktdaten.

        Args:
            image_paths: Pfade zu 1-3 Produktbildern
            api_key: Optionaler API-Key (überschreibt Konstruktor)

        Returns:
            VisionResult mit Produktinfos und Confidence
        """
        if not image_paths or len(image_paths) > 3:
            return VisionResult(
                warnings=["Es müssen 1-3 Bilder bereitgestellt werden."],
                confidence=0.0,
            )

        client = self._client
        if api_key:
            client = OpenAI(api_key=api_key)
        if not client:
            logger.warning("Kein OpenAI API-Key konfiguriert. Simuliere Vision-Output.")
            return self._fallback_result(image_paths)

        try:
            content = self._build_content(image_paths)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": VISION_SYSTEM_PROMPT},
                    {"role": "user", "content": content},
                ],
                max_tokens=500,
            )
            text = response.choices[0].message.content or "{}"
            return self._parse_response(text, image_paths)
        except Exception as e:
            logger.exception("Vision API Fehler: %s", e)
            return VisionResult(
                warnings=[f"Vision-Analyse fehlgeschlagen: {str(e)}"],
                confidence=0.0,
            )

    def _build_content(self, image_paths: list[Union[str, Path]]) -> list:
        content = []
        for path in image_paths[:3]:
            p = Path(path)
            if not p.exists():
                continue
            with open(p, "rb") as f:
                data = base64.b64encode(f.read()).decode("utf-8")
            ext = p.suffix.lower()
            mime = "image/jpeg" if ext in (".jpg", ".jpeg") else "image/png"
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:{mime};base64,{data}"},
            })
        content.append({
            "type": "text",
            "text": "Analysiere diese Produktbilder und liefere das JSON-Format.",
        })
        return content

    def _parse_response(self, text: str, image_paths: list) -> VisionResult:
        text = text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()

        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            return VisionResult(
                warnings=[f"Ungültige JSON-Antwort: {e}"],
                confidence=0.0,
            )

        warnings = []
        confidence = float(data.get("confidence", 0.0))
        if confidence < MIN_CONFIDENCE_THRESHOLD:
            warnings.append(
                f"Confidence {confidence:.2f} unter Schwellwert {MIN_CONFIDENCE_THRESHOLD}. "
                "Manuelle Prüfung empfohlen."
            )

        try:
            return VisionResult(
                product_name=str(data.get("product_name", "")),
                brand=str(data.get("brand", "")),
                model=str(data.get("model", "")),
                category=str(data.get("category", "")),
                condition=str(data.get("condition", "")),
                confidence=confidence,
                warnings=warnings,
            )
        except ValidationError as e:
            return VisionResult(
                warnings=[f"Validierungsfehler: {e}"],
                confidence=0.0,
            )

    def _fallback_result(self, image_paths: list) -> VisionResult:
        """Fallback wenn keine API verfügbar."""
        return VisionResult(
            product_name="Unbekannt (kein API-Key)",
            brand="Unbekannt",
            model="Unbekannt",
            category="Unbekannt",
            condition="Gebraucht - Gut",
            confidence=0.0,
            warnings=["Vision API nicht konfiguriert. OPENAI_API_KEY setzen."],
        )
