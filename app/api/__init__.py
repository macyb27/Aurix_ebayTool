"""API Router."""

from fastapi import APIRouter

from app.api import products, listings, pricing, market, vision, ai

api_router = APIRouter()

api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(listings.router, prefix="/listings", tags=["listings"])
api_router.include_router(pricing.router, prefix="/pricing", tags=["pricing"])
api_router.include_router(market.router, prefix="/market", tags=["market"])
api_router.include_router(vision.router, prefix="/vision", tags=["vision"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
