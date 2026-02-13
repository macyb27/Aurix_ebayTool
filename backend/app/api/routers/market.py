"""Market API router."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_market_service, get_tenant_id
from app.core.database import DbSession
from app.schemas.market import CategoryResponse, CreateCategoryRequest
from app.services.market_service import MarketService

router = APIRouter(prefix="/market", tags=["Market"])


@router.get("/categories", response_model=list[CategoryResponse])
async def get_categories(
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    db: DbSession,
    parent_id: UUID | None = Query(None, alias="parentId"),
):
    """Get categories for tenant."""
    service = get_market_service(db)
    categories = await service.get_categories(
        tenant_id, parent_id=parent_id, include_ebay_mapping=True
    )
    return [CategoryResponse(**c) for c in categories]


@router.post("/categories", response_model=CategoryResponse)
async def create_category(
    body: CreateCategoryRequest,
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
    db: DbSession,
):
    """Create category."""
    service = get_market_service(db)
    category = await service.create_category(
        tenant_id=tenant_id,
        name=body.name,
        parent_id=body.parentId,
        ebay_category_id=body.ebayCategoryId,
    )
    await db.flush()
    return CategoryResponse(
        id=str(category.id),
        name=category.name,
        parentId=str(category.parent_id) if category.parent_id else None,
        ebayCategoryId=category.ebay_category_id,
    )


@router.get("/ebay/categories")
async def search_ebay_categories(
    db: DbSession,
    q: str = Query(..., min_length=1),
    marketplace_id: str = Query("EBAY_DE", alias="marketplaceId"),
):
    """Search eBay categories."""
    service = get_market_service(db)
    return await service.search_ebay_categories(q, marketplace_id)
