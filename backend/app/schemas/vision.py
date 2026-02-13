"""Vision/AI schemas."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel


class AnalyzeImagesRequest(BaseModel):
    """Analyze images request."""

    images: list[str]
    productName: Optional[str] = None
    listingId: Optional[UUID] = None


class GenerateDescriptionRequest(BaseModel):
    """Generate description request."""

    productName: str
    productAttributes: dict[str, Any] = {}
    images: list[str] = []
    targetLength: str = "medium"
    language: str = "de"


class AIJobResult(BaseModel):
    """AI job result."""

    title: Optional[str] = None
    description: Optional[str] = None
    suggestedCategory: Optional[str] = None
    tags: Optional[list[str]] = None


class AIJobResponse(BaseModel):
    """AI job response."""

    id: UUID
    status: str
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    createdAt: datetime
    completedAt: Optional[datetime] = None

    model_config = {"from_attributes": True}
