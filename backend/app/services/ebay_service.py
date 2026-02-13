"""EbayService - eBay API integration, token handling, publish."""

import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.ebay import EbayAccount, EbayListingMapping, SyncJob
from app.services.ebay_client import EbayClient

logger = logging.getLogger(__name__)
settings = get_settings()


class EbayService:
    """eBay integration service - token, publish, sync."""

    def __init__(self, db: AsyncSession, ebay_client: Optional[EbayClient] = None):
        self.db = db
        self.ebay_client = ebay_client or EbayClient()

    async def get_or_refresh_token(
        self, ebay_account_id: UUID, tenant_id: UUID
    ) -> Optional[str]:
        """Get valid access token, refreshing if needed."""
        account = await self._get_account(ebay_account_id, tenant_id)
        if not account or not account.refresh_token_encrypted:
            return None

        # Check if token is still valid (with 5 min buffer)
        if (
            account.token_expires_at
            and account.token_expires_at > datetime.now(timezone.utc) + timedelta(minutes=5)
        ):
            # In production: decrypt access_token_encrypted
            return account.access_token_encrypted

        try:
            # In production: decrypt refresh_token_encrypted
            refresh_token = account.refresh_token_encrypted
            access_token = await self.ebay_client.get_access_token(refresh_token)
            # In production: encrypt and store new token
            account.access_token_encrypted = access_token
            account.token_expires_at = datetime.now(timezone.utc) + timedelta(hours=2)
            await self.db.flush()
            return access_token
        except Exception as e:
            logger.exception("Token refresh failed: %s", e)
            return None

    async def create_publish_job(
        self,
        listing_id: UUID,
        tenant_id: UUID,
        ebay_account_id: UUID,
    ) -> SyncJob:
        """Create sync job for publishing listing to eBay."""
        job = SyncJob(
            listing_id=listing_id,
            ebay_account_id=ebay_account_id,
            status="queued",
        )
        self.db.add(job)
        await self.db.flush()
        return job

    async def get_sync_status(
        self, listing_id: UUID, tenant_id: UUID
    ) -> Optional[dict]:
        """Get sync status for listing."""
        result = await self.db.execute(
            select(SyncJob)
            .where(SyncJob.listing_id == listing_id)
            .order_by(SyncJob.created_at.desc())
            .limit(1)
        )
        job = result.scalar_one_or_none()
        if not job:
            return None

        # Verify account belongs to tenant
        account = await self._get_account(job.ebay_account_id, tenant_id)
        if not account:
            return None

        return {
            "listingId": str(listing_id),
            "status": job.status,
            "ebayItemId": job.ebay_item_id,
            "ebayUrl": job.ebay_url,
            "lastError": job.error_message,
            "updatedAt": job.completed_at or job.created_at,
        }

    async def get_ebay_mapping(
        self, listing_id: UUID, tenant_id: UUID
    ) -> Optional[EbayListingMapping]:
        """Get eBay listing mapping if published."""
        result = await self.db.execute(
            select(EbayListingMapping).where(EbayListingMapping.listing_id == listing_id)
        )
        mapping = result.scalar_one_or_none()
        if not mapping:
            return None
        account = await self._get_account(mapping.ebay_account_id, tenant_id)
        if not account:
            return None
        return mapping

    async def _get_account(
        self, account_id: UUID, tenant_id: UUID
    ) -> Optional[EbayAccount]:
        """Get eBay account by ID with tenant check."""
        result = await self.db.execute(
            select(EbayAccount).where(
                EbayAccount.id == account_id,
                EbayAccount.tenant_id == tenant_id,
            )
        )
        return result.scalar_one_or_none()
