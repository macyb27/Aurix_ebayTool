"""Common schemas."""

from typing import Any, Optional

from pydantic import BaseModel, Field


class PaginationMeta(BaseModel):
    """Pagination metadata."""

    page: int = 1
    perPage: int = 20
    total: int = 0
    totalPages: int = 0


class PaginationLinks(BaseModel):
    """Pagination links."""

    self: str
    next: Optional[str] = None
    prev: Optional[str] = None


class ErrorDetail(BaseModel):
    """Validation error detail."""

    field: str
    message: str


class RFC7807Error(BaseModel):
    """RFC 7807 problem detail."""

    type: str
    title: str
    status: int
    detail: str
    instance: Optional[str] = None
    traceId: Optional[str] = None
    errors: Optional[list[ErrorDetail]] = None
