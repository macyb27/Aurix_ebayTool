"""Listing API router."""

from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_ebay_service, get_listing_service, get_tenant_id
from app.core.database import DbSession
from app.core.exceptions import NotFoundError, ValidationError
from app.schemas.common import PaginationLinks, PaginationMeta
from app.schemas.listing import (
    CreateListingRequest,
    GenerateAIRequest,
    ListingResponse,
    ListingWorkflow,
    UpdateListingRequest,
)
from app.services.listing_service import ListingService

router = APIRouter(prefix="/listings", tags=["Listings"])


def _listing_to_response(listing) -> ListingResponse:
    """Convert Listing model to response."""
    return ListingResponse(
        id=listing.id,
        status=listing.status,
        productId=listing.product_id,
        title=listing.title,
        description=listing.description,
        price=float(listing.price),
        quantity=listing.quantity,
        workflow=ListingWorkflow(
            currentStep=listing.workflow_step,
            nextSteps=[],  # Filled below
        ),
        createdAt=listing.created_at,
        updatedAt=listing.updated_at,
    )


@router.get("", response_model=dict)
async def list_listings(
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    db: DbSession,
    status_filter: str | None = None,
    page: int = 1,
    per_page: int = 20,
):
    """List listings with pagination."""
    service = get_listing_service(db)
    listings, total = await service.list_listings(
        tenant_id, status=status_filter, page=page, per_page=per_page
    )
    total_pages = (total + per_page - 1) // per_page if total else 0
    base = f"/v1/listings?page={page}&perPage={per_page}"
    return {
        "data": [_listing_to_response(l) for l in listings],
        "meta": PaginationMeta(
            page=page,
            perPage=per_page,
            total=total,
            totalPages=total_pages,
        ),
        "links": PaginationLinks(
            self=base,
            next=f"/v1/listings?page={page+1}&perPage={per_page}" if page < total_pages else None,
            prev=f"/v1/listings?page={page-1}&perPage={per_page}" if page > 1 else None,
        ),
    }


@router.post("", response_model=ListingResponse, status_code=status.HTTP_201_CREATED)
async def create_listing(
    body: CreateListingRequest,
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    db: DbSession,
):
    """Create listing draft."""
    service = get_listing_service(db)
    shipping = [s.model_dump() for s in body.shippingOptions]
    listing = await service.create_listing(
        tenant_id=tenant_id,
        product_id=body.productId,
        title=body.title,
        description=body.description,
        price=body.price,
        quantity=body.quantity,
        template_id=body.templateId,
        category_id=body.categoryId,
        condition=body.condition,
        images=body.images,
        duration=body.duration,
        payment_methods=body.paymentMethods,
        shipping_options=shipping,
    )
    resp = _listing_to_response(listing)
    next_steps = await service.get_workflow_next_steps(listing.status)
    resp.workflow.nextSteps = next_steps
    return resp


@router.get("/{listing_id}", response_model=ListingResponse)
async def get_listing(
    listing_id: UUID,
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    db: DbSession,
):
    """Get listing by ID."""
    service = get_listing_service(db)
    listing = await service.get_listing(listing_id, tenant_id)
    if not listing:
        raise NotFoundError("Listing not found")
    resp = _listing_to_response(listing)
    resp.workflow.nextSteps = await service.get_workflow_next_steps(listing.status)
    return resp


@router.patch("/{listing_id}", response_model=ListingResponse)
async def update_listing(
    listing_id: UUID,
    body: UpdateListingRequest,
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    db: DbSession,
):
    """Update listing (draft only)."""
    service = get_listing_service(db)
    updates = body.model_dump(exclude_none=True)
    listing = await service.update_listing(listing_id, tenant_id, **updates)
    if not listing:
        raise NotFoundError("Listing not found or not editable")
    return _listing_to_response(listing)


@router.post("/{listing_id}/approve", response_model=ListingResponse)
async def approve_listing(
    listing_id: UUID,
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    db: DbSession,
    # In production: approved_by from JWT
):
    """Approve listing for publish."""
    service = get_listing_service(db)
    listing = await service.approve_listing(
        listing_id, tenant_id, approved_by=tenant_id
    )
    if not listing:
        raise NotFoundError("Listing not found or not in draft status")
    resp = _listing_to_response(listing)
    resp.workflow.nextSteps = ["publish"]
    return resp


@router.post("/{listing_id}/generate-ai", status_code=status.HTTP_202_ACCEPTED)
async def generate_ai(
    listing_id: UUID,
    body: GenerateAIRequest,
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    db: DbSession,
):
    """Trigger AI generation for listing (async, returns job ID)."""
    from app.tasks.ai_tasks import generate_listing_ai_task

    service = get_listing_service(db)
    listing = await service.get_listing(listing_id, tenant_id)
    if not listing:
        raise NotFoundError("Listing not found")
    if listing.status != "draft":
        raise ValidationError("Only draft listings can use AI generation")

    # Queue Celery task
    task = generate_listing_ai_task.delay(
        str(listing_id),
        str(tenant_id),
        str(body.productId),
        body.fields,
    )
    return {
        "jobId": task.id,
        "status": "pending",
        "estimatedCompletion": datetime.now(timezone.utc).isoformat(),
    }


class PublishRequest(BaseModel):
    """Publish request body."""

    ebayAccountId: UUID


@router.post("/{listing_id}/publish", status_code=status.HTTP_202_ACCEPTED)
async def publish_listing(
    listing_id: UUID,
    body: PublishRequest,
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    db: DbSession,
):
    """Publish listing to eBay (async)."""
    from app.tasks.sync_tasks import publish_listing_task

    service = get_listing_service(db)
    ebay_service = get_ebay_service(db)
    listing = await service.get_listing(listing_id, tenant_id)
    if not listing:
        raise NotFoundError("Listing not found")
    if listing.status != "approved":
        raise ValidationError("Listing must be approved before publish")

    ebay_account_id = body.ebayAccountId
    sync_job = await ebay_service.create_publish_job(
        listing_id, tenant_id, ebay_account_id
    )
    task = publish_listing_task.delay(
        str(sync_job.id),
        str(listing_id),
        str(tenant_id),
        str(ebay_account_id),
    )
    return {
        "id": str(listing_id),
        "status": "publishing",
        "syncJobId": str(sync_job.id),
    }
