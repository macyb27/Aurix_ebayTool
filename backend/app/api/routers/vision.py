"""Vision/AI API router."""

from uuid import UUID

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import get_tenant_id, get_vision_service
from app.core.database import DbSession
from app.core.exceptions import NotFoundError
from app.schemas.vision import (
    AIJobResponse,
    AnalyzeImagesRequest,
    GenerateDescriptionRequest,
)
from app.services.vision_service import VisionService

router = APIRouter(prefix="/ai", tags=["AI / Vision"])


@router.post("/analyze-images")
async def analyze_images(
    body: AnalyzeImagesRequest,
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    db: DbSession,
):
    """Analyze product images for categories and tags."""
    service = get_vision_service(db)
    return await service.analyze_images(
        tenant_id=tenant_id,
        images=body.images,
        product_name=body.productName,
        listing_id=body.listingId,
    )


@router.post("/generate-description")
async def generate_description(
    body: GenerateDescriptionRequest,
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    db: DbSession,
):
    """Generate listing title and description."""
    service = get_vision_service(db)
    return await service.generate_description(
        tenant_id=tenant_id,
        product_name=body.productName,
        product_attributes=body.productAttributes,
        images=body.images,
        target_length=body.targetLength,
        language=body.language,
    )


@router.get("/jobs/{job_id}", response_model=AIJobResponse)
async def get_ai_job(
    job_id: UUID,
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    db: DbSession,
):
    """Get AI job status and result."""
    service = get_vision_service(db)
    job = await service.get_job(job_id, tenant_id)
    if not job:
        raise NotFoundError("AI job not found")
    return AIJobResponse(
        id=job.id,
        status=job.status,
        result=job.output_payload,
        error=job.error_message,
        createdAt=job.created_at,
        completedAt=job.completed_at,
    )
