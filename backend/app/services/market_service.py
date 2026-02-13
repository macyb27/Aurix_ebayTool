"""MarketService - eBay market data, categories, marketplace info."""

import logging
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory import Category
from app.services.ebay_client import EbayClient

logger = logging.getLogger(__name__)


class MarketService:
    """Market/category service for eBay marketplace data."""

    def __init__(self, db: AsyncSession, ebay_client: Optional[EbayClient] = None):
        self.db = db
        self.ebay_client = ebay_client or EbayClient()

    async def get_categories(
        self,
        tenant_id: UUID,
        parent_id: Optional[UUID] = None,
        include_ebay_mapping: bool = True,
    ) -> list[dict[str, Any]]:
        """Get categories for tenant, optionally filtered by parent."""
        query = select(Category).where(Category.tenant_id == tenant_id)
        if parent_id is not None:
            query = query.where(Category.parent_id == parent_id)
        else:
            query = query.where(Category.parent_id.is_(None))

        result = await self.db.execute(query)
        categories = result.scalars().all()

        return [
            {
                "id": str(c.id),
                "name": c.name,
                "parentId": str(c.parent_id) if c.parent_id else None,
                "ebayCategoryId": c.ebay_category_id if include_ebay_mapping else None,
            }
            for c in categories
        ]

    async def get_ebay_category_tree(
        self, marketplace_id: str = "EBAY_DE"
    ) -> dict[str, Any]:
        """Fetch eBay category tree from API."""
        try:
            return await self.ebay_client.get_categories(marketplace_id)
        except Exception as e:
            logger.warning("eBay category fetch failed: %s", e)
            return {"categories": [], "categoryTreeId": marketplace_id}

    async def create_category(
        self,
        tenant_id: UUID,
        name: str,
        parent_id: Optional[UUID] = None,
        ebay_category_id: Optional[str] = None,
    ) -> Category:
        """Create category for tenant."""
        category = Category(
            tenant_id=tenant_id,
            name=name,
            parent_id=parent_id,
            ebay_category_id=ebay_category_id,
        )
        self.db.add(category)
        await self.db.flush()
        return category

    async def get_category_by_id(
        self, category_id: UUID, tenant_id: UUID
    ) -> Optional[Category]:
        """Get category by ID."""
        result = await self.db.execute(
            select(Category).where(
                Category.id == category_id,
                Category.tenant_id == tenant_id,
            )
        )
        return result.scalar_one_or_none()

    async def search_ebay_categories(
        self, query: str, marketplace_id: str = "EBAY_DE"
    ) -> list[dict[str, Any]]:
        """Search eBay categories by name (simplified - uses tree)."""
        tree = await self.get_ebay_category_tree(marketplace_id)
        categories = tree.get("categoryTreeNode", {}).get("childCategoryTreeNodes", [])
        query_lower = query.lower()
        results = []

        def search_recursive(nodes: list, path: str = "") -> None:
            for node in nodes:
                name = node.get("category", {}).get("name", "")
                cat_id = node.get("category", {}).get("categoryId", "")
                full_path = f"{path}/{name}" if path else name
                if query_lower in name.lower():
                    results.append({
                        "id": cat_id,
                        "name": name,
                        "path": full_path,
                    })
                children = node.get("childCategoryTreeNodes", [])
                if children:
                    search_recursive(children, full_path)

        search_recursive(categories)
        return results[:20]
