"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routers import listings, market, pricing, sync, vision
from app.core.config import get_settings
from app.core.database import engine
from app.core.exceptions import AppException
from app.core.exceptions import rfc7807_error

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(listings.router, prefix="/v1")
app.include_router(vision.router, prefix="/v1")
app.include_router(market.router, prefix="/v1")
app.include_router(pricing.router, prefix="/v1")
app.include_router(sync.router, prefix="/v1")


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle application exceptions with RFC 7807 format."""
    return JSONResponse(
        status_code=exc.status_code,
        content=rfc7807_error(
            type_uri=exc.error_type,
            title=exc.__class__.__name__,
            status_code=exc.status_code,
            detail=exc.message,
            instance=str(request.url.path),
            trace_id=request.headers.get("X-Request-Id"),
            errors=exc.errors,
        ),
    )


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}
