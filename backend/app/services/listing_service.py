"""ListingService - Listing lifecycle and workflow."""

import logging
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.listing import Listing, ListingHistory, ListingTemplate

logger = logging.getLogger(__name__)


class ListingService:
    """Listing lifecycle service."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_listing(
        self,
        tenant_id: UUID,
        product_id: UUID,
        title: str,
        description: str,
        price: float,
        quantity: int,
        *,
        template_id: Optional[UUID] = None,
        category_id: Optional[str] = None,
        condition: Optional[str] = None,
        images: Optional[list[str]] = None,
        duration: Optional[str] = None,
        payment_methods: Optional[list[str]] = None,
        shipping_options: Optional[list[dict]] = None,
        created_by: Optional[UUID] = None,
    ) -> Listing:
        """Create listing draft."""
        listing = Listing(
            tenant_id=tenant_id,
            product_id=product_id,
            template_id=template_id,
            title=title,
            description=description,
            price=price,
            quantity=quantity,
            category_id=category_id,
            condition=condition or "new",
            images=images or [],
            duration=duration or "GTC",
            payment_methods=payment_methods or ["PayPal"],
            shipping_options=shipping_options or [],
            status="draft",
            workflow_step="draft",
            created_by=created_by,
        )
        self.db.add(listing)
        await self.db.flush()
        await self._add_history(listing.id, "created", {"status": "draft"})
        return listing

    async def get_listing(
        self, listing_id: UUID, tenant_id: UUID
    ) -> Optional[Listing]:
        """Get listing by ID."""
        result = await self.db.execute(
            select(Listing).where(
                Listing.id == listing_id,
                Listing.tenant_id == tenant_id,
                Listing.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list_listings(
        self,
        tenant_id: UUID,
        status: Optional[str] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[Listing], int]:
        """List listings with pagination."""
        query = select(Listing).where(
            Listing.tenant_id == tenant_id,
            Listing.deleted_at.is_(None),
        )
        count_query = select(func.count(Listing.id)).where(
            Listing.tenant_id == tenant_id,
            Listing.deleted_at.is_(None),
        )
        if status:
            query = query.where(Listing.status == status)
            count_query = count_query.where(Listing.status == status)

        total_result = await self.db.execute(count_query)
        total_count = total_result.scalar() or 0

        query = query.offset((page - 1) * per_page).limit(per_page)
        result = await self.db.execute(query)
        listings = result.scalars().all()
        return list(listings), total_count

    async def approve_listing(
        self, listing_id: UUID, tenant_id: UUID, approved_by: UUID
    ) -> Optional[Listing]:
        """Approve listing for publish."""
        listing = await self.get_listing(listing_id, tenant_id)
        if not listing or listing.status != "draft":
            return None
        listing.status = "approved"
        listing.workflow_step = "approved"
        listing.approved_by = approved_by
        listing.approved_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self._add_history(listing.id, "approved", {"approved_by": str(approved_by)})
        return listing

    async def update_listing(
        self,
        listing_id: UUID,
        tenant_id: UUID,
        **updates: Any,
    ) -> Optional[Listing]:
        """Update listing (draft only)."""
        listing = await self.get_listing(listing_id, tenant_id)
        if not listing or listing.status != "draft":
            return None
        for key, value in updates.items():
            if hasattr(listing, key):
                setattr(listing, key, value)
        await self.db.flush()
        await self._add_history(listing.id, "updated", updates)
        return listing

    async def _add_history(
        self, listing_id: UUID, event_type: str, payload: dict
    ) -> None:
        """Add listing history entry."""
        history = ListingHistory(
            listing_id=listing_id,
            event_type=event_type,
            payload=payload,
        )
        self.db.add(history)
        await self.db.flush()

    async def get_workflow_next_steps(self, status: str) -> list[str]:
        """Get next workflow steps for status."""
        steps = {
            "draft": ["review", "publish"],
            "approved": ["publish"],
            "publishing": [],
            "published": [],
            "failed": ["retry"],
        }
        return steps.get(status, [])

    # Templates
    async def create_template(
        self,
        tenant_id: UUID,
        name: str,
        *,
        title_template: Optional[str] = None,
        description_template: Optional[str] = None,
        default_duration: Optional[str] = None,
        default_payment_methods: Optional[list] = None,
        default_shipping_options: Optional[list] = None,
    ) -> ListingTemplate:
        """Create listing template."""
        template = ListingTemplate(
            tenant_id=tenant_id,
            name=name,
            title_template=title_template,
            description_template=description_template,
            default_duration=default_duration or "GTC",
            default_payment_methods=default_payment_methods or ["PayPal"],
            default_shipping_options=default_shipping_options or [],
        )
        self.db.add(template)
        await self.db.flush()
        return template

    async def get_template(
        self, template_id: UUID, tenant_id: UUID
    ) -> Optional[ListingTemplate]:
        """Get template by ID."""
        result = await self.db.execute(
            select(ListingTemplate).where(
                ListingTemplate.id == template_id,
                ListingTemplate.tenant_id == tenant_id,
                ListingTemplate.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()
