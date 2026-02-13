"""AI/Vision Celery tasks."""

from uuid import UUID

from app.tasks.celery_app import celery_app


@celery_app.task(bind=True, max_retries=3)
def generate_listing_ai_task(
    self,
    listing_id: str,
    tenant_id: str,
    product_id: str,
    fields: list[str],
):
    """
    Background task: Generate AI content for listing.
    In production: uses async DB session, calls VisionService.
    """
    # Placeholder: In production, use sync DB session and VisionService
    return {
        "listingId": listing_id,
        "tenantId": tenant_id,
        "productId": product_id,
        "fields": fields,
        "status": "queued",
    }
