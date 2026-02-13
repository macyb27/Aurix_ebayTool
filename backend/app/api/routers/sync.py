"""Sync/eBay API router."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import get_ebay_service, get_tenant_id
from app.core.database import DbSession
from app.core.exceptions import NotFoundError
from app.services.ebay_service import EbayService

router = APIRouter(prefix="/sync", tags=["Sync"])


@router.get("/status/{listing_id}")
async def get_sync_status(
    listing_id: UUID,
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    db: DbSession,
):
    """Get sync status for listing."""
    service = get_ebay_service(db)
    status_data = await service.get_sync_status(listing_id, tenant_id)
    if not status_data:
        raise NotFoundError("Sync status not found for listing")
    return status_data
