"""Celery Tasks für Listing-Operationen."""

import asyncio
import logging

from app.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def create_listing_task(self, listing_id: int, user_id: str) -> dict:
    """Background Task: Listing bei eBay erstellen."""
    try:
        from app.database import async_session_maker
        from sqlalchemy import select
        from app.models import Listing
        from app.services.listing_service import ListingService

        async def _create():
            async with async_session_maker() as session:
                result = await session.execute(select(Listing).where(Listing.id == listing_id))
                listing = result.scalar_one_or_none()
                if not listing:
                    raise ValueError(f"Listing {listing_id} not found")
                service = ListingService(session)
                await service.publish_to_ebay(listing_id, user_id)
                return {"status": "published", "listing_id": listing_id}

        return asyncio.run(_create())
    except Exception as exc:
        logger.exception("create_listing_task failed")
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3)
def analyze_product_task(self, image_url: str) -> dict:
    """Background Task: Produkt aus Bild analysieren."""
    try:
        from app.services.vision_service import VisionService

        service = VisionService()
        return asyncio.run(service.analyze_image(image_url))
    except Exception as exc:
        logger.exception("analyze_product_task failed")
        raise self.retry(exc=exc)
