"""FastAPI Application - AURIX Backend."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.config import get_settings
from app.core.exceptions import (
    AurixError,
    EbayApiError,
    EbayTokenError,
    VisionServiceError,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application Lifespan."""
    logger.info("AURIX Backend starting")
    yield
    logger.info("AURIX Backend shutting down")


app = FastAPI(
    title=get_settings().app_name,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(EbayApiError)
async def ebay_api_error_handler(request: Request, exc: EbayApiError):
    """eBay API Fehler."""
    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=exc.status_code or 502,
        content={"detail": str(exc), "type": "ebay_api_error"},
    )


@app.exception_handler(EbayTokenError)
async def ebay_token_error_handler(request: Request, exc: EbayTokenError):
    """eBay Token Fehler."""
    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=401,
        content={"detail": str(exc), "type": "ebay_token_error"},
    )


@app.exception_handler(VisionServiceError)
async def vision_error_handler(request: Request, exc: VisionServiceError):
    """Vision Service Fehler."""
    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "type": "vision_error"},
    )


@app.exception_handler(AurixError)
async def aurix_error_handler(request: Request, exc: AurixError):
    """Allgemeine AURIX Fehler."""
    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=400,
        content={"detail": str(exc), "type": "aurix_error"},
    )


app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health():
    """Health Check."""
    return {"status": "ok"}

