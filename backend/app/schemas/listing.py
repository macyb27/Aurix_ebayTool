"""Listing schemas."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ShippingOption(BaseModel):
    """Shipping option."""

    type: str = "flat"
    cost: float = 0.0
    domesticOnly: bool = True


class CreateListingRequest(BaseModel):
    """Create listing request."""

    productId: UUID
    templateId: Optional[UUID] = None
    title: str = Field(..., min_length=10, max_length=80)
    description: str
    price: float = Field(..., ge=0)
    quantity: int = Field(..., ge=1)
    categoryId: Optional[str] = None
    condition: str = "new"
    images: list[str] = []
    duration: str = "GTC"
    paymentMethods: list[str] = ["PayPal"]
    shippingOptions: list[ShippingOption] = []


class UpdateListingRequest(BaseModel):
    """Update listing request."""

    title: Optional[str] = Field(None, min_length=10, max_length=80)
    description: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    quantity: Optional[int] = Field(None, ge=1)
    images: Optional[list[str]] = None


class ListingWorkflow(BaseModel):
    """Listing workflow info."""

    currentStep: str
    nextSteps: list[str]


class ListingResponse(BaseModel):
    """Listing response."""

    id: UUID
    status: str
    productId: UUID
    title: str
    description: str
    price: float
    quantity: int
    workflow: Optional[ListingWorkflow] = None
    createdAt: datetime
    updatedAt: datetime

    model_config = {"from_attributes": True}


class GenerateAIRequest(BaseModel):
    """Generate AI request."""

    fields: list[str] = ["title", "description", "category"]
    productId: UUID


class GenerateAIResponse(BaseModel):
    """Generate AI response (202)."""

    jobId: UUID
    status: str = "pending"
    estimatedCompletion: Optional[datetime] = None
