"""Market schemas."""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class CategoryResponse(BaseModel):
    """Category response."""

    id: str
    name: str
    parentId: Optional[str] = None
    ebayCategoryId: Optional[str] = None


class CreateCategoryRequest(BaseModel):
    """Create category request."""

    name: str
    parentId: Optional[UUID] = None
    ebayCategoryId: Optional[str] = None
