"""Sync/eBay Celery tasks."""

from app.tasks.celery_app import celery_app


@celery_app.task(bind=True, max_retries=5)
def publish_listing_task(
    self,
    sync_job_id: str,
    listing_id: str,
    tenant_id: str,
    ebay_account_id: str,
):
    """
    Background task: Publish listing to eBay.
    In production: loads listing, gets token, calls eBay API.
    """
    # Placeholder: In production, use sync DB and EbayService
    return {
        "syncJobId": sync_job_id,
        "listingId": listing_id,
        "status": "queued",
    }
