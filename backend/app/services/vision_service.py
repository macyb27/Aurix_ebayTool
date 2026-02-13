"""VisionService - AI image analysis and description generation (AI Service)."""

import logging
from typing import Any, Optional
from uuid import UUID

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.ai import AIJob

logger = logging.getLogger(__name__)
settings = get_settings()


class VisionService:
    """AI/Vision service for image analysis and description generation."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def analyze_images(
        self,
        tenant_id: UUID,
        images: list[str],
        product_name: Optional[str] = None,
        listing_id: Optional[UUID] = None,
    ) -> dict[str, Any]:
        """
        Analyze product images for categories, tags, and attributes.
        Returns suggested category, tags, and product attributes.
        """
        job = AIJob(
            tenant_id=tenant_id,
            listing_id=listing_id,
            job_type="analyze_images",
            status="processing",
            input_payload={
                "images": images,
                "product_name": product_name,
            },
        )
        self.db.add(job)
        await self.db.flush()

        try:
            result = await self._call_vision_api(images, product_name)
            job.status = "completed"
            job.output_payload = result
            await self.db.flush()
            return result
        except Exception as e:
            logger.exception("Vision API failed: %s", e)
            job.status = "failed"
            job.error_message = str(e)
            await self.db.flush()
            raise

    async def generate_description(
        self,
        tenant_id: UUID,
        product_name: str,
        product_attributes: dict[str, Any],
        images: list[str],
        target_length: str = "medium",
        language: str = "de",
        listing_id: Optional[UUID] = None,
    ) -> dict[str, Any]:
        """Generate listing title and description using AI."""
        job = AIJob(
            tenant_id=tenant_id,
            listing_id=listing_id,
            job_type="generate_description",
            status="processing",
            input_payload={
                "product_name": product_name,
                "product_attributes": product_attributes,
                "images": images,
                "target_length": target_length,
                "language": language,
            },
        )
        self.db.add(job)
        await self.db.flush()

        try:
            result = await self._call_description_api(
                product_name, product_attributes, target_length, language
            )
            job.status = "completed"
            job.output_payload = result
            await self.db.flush()
            return result
        except Exception as e:
            logger.exception("Description generation failed: %s", e)
            job.status = "failed"
            job.error_message = str(e)
            await self.db.flush()
            raise

    async def _call_vision_api(
        self, images: list[str], product_name: Optional[str]
    ) -> dict[str, Any]:
        """Call AI vision API (OpenAI-compatible) for image analysis."""
        if not settings.ai_api_key:
            return self._mock_vision_response(images, product_name)

        # Simplified: use OpenAI vision or similar
        # In production: use actual vision API
        return self._mock_vision_response(images, product_name)

    async def _call_description_api(
        self,
        product_name: str,
        attributes: dict[str, Any],
        target_length: str,
        language: str,
    ) -> dict[str, Any]:
        """Call AI API for description generation."""
        if not settings.ai_api_key:
            return self._mock_description_response(product_name, attributes)

        # In production: call OpenAI/Anthropic
        return self._mock_description_response(product_name, attributes)

    def _mock_vision_response(
        self, images: list[str], product_name: Optional[str]
    ) -> dict[str, Any]:
        """Mock response when AI not configured."""
        return {
            "suggestedCategory": "9355",  # eBay category placeholder
            "tags": ["product", product_name or "item"] if product_name else ["product"],
            "attributes": {},
        }

    def _mock_description_response(
        self, product_name: str, attributes: dict[str, Any]
    ) -> dict[str, Any]:
        """Mock response when AI not configured."""
        attrs_str = ", ".join(f"{k}: {v}" for k, v in attributes.items()) or "hochwertig"
        return {
            "title": product_name[:80] if len(product_name) > 80 else product_name,
            "description": f"<p>{product_name}</p><p>Eigenschaften: {attrs_str}</p>",
            "suggestedCategory": "9355",
            "tags": [product_name.replace(" ", "-").lower(), "neu"],
        }

    async def get_job(self, job_id: UUID, tenant_id: UUID) -> Optional[AIJob]:
        """Get AI job by ID."""
        result = await self.db.execute(
            select(AIJob).where(
                AIJob.id == job_id,
                AIJob.tenant_id == tenant_id,
            )
        )
        return result.scalar_one_or_none()
