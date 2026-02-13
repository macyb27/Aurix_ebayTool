"""AI Integration Service - LLM-Aufruf, Validierung, Persistierung."""

import json
import logging
from typing import Any

from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config import get_settings
from app.core.exceptions import ValidationError
from app.models.ai_result import AIResult
from app.schemas.ai_results import FullAIResult

logger = logging.getLogger(__name__)

FULL_AI_RESULT_JSON_SCHEMA = """
Antworte NUR mit gültigem JSON in folgender Struktur (kein anderer Text):
{
  "vision": {
    "title": "string",
    "description": "string oder null",
    "category_hint": "string oder null",
    "condition": "string oder null",
    "estimated_price": number oder null,
    "brand": "string oder null",
    "confidence": 0.0-1.0
  },
  "market": {
    "category_id": "string",
    "search_term": "string oder null",
    "avg_sold_price": number oder null,
    "sold_count": int oder null,
    "active_listings": int oder null,
    "demand_score": 0-100 oder null,
    "confidence": 0.0-1.0
  },
  "pricing": {
    "avg_price": number,
    "min_price": number,
    "max_price": number,
    "recommended_price": number,
    "sample_count": int,
    "confidence": 0.0-1.0
  },
  "listing": {
    "title": "string",
    "description": "string oder null",
    "price": number,
    "category_id": "string oder null",
    "strategy": "auction" oder "fixed",
    "duration": "string oder null",
    "confidence": 0.0-1.0
  }
}
"""


class AIIntegrationService:
    """Service für AI-Agent-Integration: LLM-Aufruf, Validierung, DB-Persistierung."""

    def __init__(self, db: AsyncSession, api_key: str | None = None):
        self._db = db
        self._api_key = api_key or get_settings().openai_api_key

    async def analyze(
        self,
        prompt: str,
        *,
        user_id: str | None = None,
        product_id: int | None = None,
    ) -> FullAIResult:
        """
        LLM aufrufen, JSON validieren, in DB speichern.
        Wirft ValidationError bei Validierungsfehler.
        Retry (max 3) bei API-Fehlern.
        """
        raw_json = await self._call_llm(prompt)
        result = self._validate_json(raw_json)
        await self._save_to_db(result, prompt=prompt, user_id=user_id, product_id=product_id)
        return result

    @retry(
        retry=retry_if_exception_type((ConnectionError, TimeoutError, OSError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    async def _call_llm(self, prompt: str) -> str:
        """LLM aufrufen. Retry bei API/Network-Fehlern (max 3)."""
        if not self._api_key:
            raise ValidationError("OpenAI API Key fehlt – LLM-Aufruf nicht möglich")

        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=self._api_key)
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": FULL_AI_RESULT_JSON_SCHEMA,
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=2000,
            )
            content = response.choices[0].message.content
            if not content:
                raise ValidationError("LLM lieferte leere Antwort")
            return content
        except (PydanticValidationError, ValidationError):
            raise
        except Exception as e:
            logger.warning("LLM API call failed: %s", e)
            raise ConnectionError(f"LLM API Fehler: {e}") from e

    def _validate_json(self, raw: str) -> FullAIResult:
        """JSON gegen FullAIResult validieren. Wirft ValidationError bei Fehler."""
        data = self._extract_json(raw)
        try:
            return FullAIResult.model_validate(data)
        except PydanticValidationError as e:
            raise ValidationError(f"FullAIResult Validierung fehlgeschlagen: {e}") from e

    def _extract_json(self, raw: str) -> dict[str, Any]:
        """JSON aus Roh-String extrahieren (inkl. Markdown-Codeblock)."""
        text = raw.strip()
        if "```" in text:
            for part in text.split("```"):
                part = part.strip()
                if part.lower().startswith("json"):
                    part = part[4:].strip()
                if part:
                    try:
                        return json.loads(part)
                    except json.JSONDecodeError:
                        continue
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Ungültiges JSON: {e}") from e

    async def _save_to_db(
        self,
        result: FullAIResult,
        *,
        prompt: str | None = None,
        user_id: str | None = None,
        product_id: int | None = None,
    ) -> AIResult:
        """Ergebnis in DB speichern."""
        record = AIResult(
            user_id=user_id,
            input_prompt=prompt,
            result_json=result.model_dump(mode="json"),
            product_id=product_id,
        )
        self._db.add(record)
        await self._db.flush()
        await self._db.refresh(record)
        return record
