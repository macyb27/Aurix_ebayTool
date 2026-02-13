"""Custom exceptions and error handling (RFC 7807)."""

from typing import Any, Optional

from fastapi import HTTPException, status


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_type: Optional[str] = None,
        errors: Optional[list[dict[str, Any]]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_type = error_type or "https://api.ebay-tool.com/errors/internal"
        self.errors = errors or []
        super().__init__(message)


class ValidationError(AppException):
    """Validation error (400)."""

    def __init__(self, message: str, errors: Optional[list[dict[str, Any]]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_type="https://api.ebay-tool.com/errors/validation",
            errors=errors or [],
        )


class NotFoundError(AppException):
    """Resource not found (404)."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_type="https://api.ebay-tool.com/errors/not-found",
        )


class UnauthorizedError(AppException):
    """Unauthorized (401)."""

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_type="https://api.ebay-tool.com/errors/unauthorized",
        )


class ForbiddenError(AppException):
    """Forbidden (403)."""

    def __init__(self, message: str = "Forbidden"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_type="https://api.ebay-tool.com/errors/forbidden",
        )


class EbayApiError(AppException):
    """eBay API error."""

    def __init__(
        self,
        message: str,
        status_code: int = 502,
        ebay_error_code: Optional[str] = None,
    ):
        error_type = "https://api.ebay-tool.com/errors/ebay-api"
        errors = []
        if ebay_error_code:
            errors.append({"field": "ebayErrorCode", "message": ebay_error_code})
        super().__init__(
            message=message,
            status_code=status_code,
            error_type=error_type,
            errors=errors,
        )


class EbayRateLimitError(EbayApiError):
    """eBay rate limit (429)."""

    def __init__(
        self,
        message: str = "eBay API rate limit exceeded",
        retry_after: int = 60,
    ):
        super().__init__(message=message, status_code=429)
        self.retry_after = retry_after


def rfc7807_error(
    type_uri: str,
    title: str,
    status_code: int,
    detail: str,
    instance: Optional[str] = None,
    trace_id: Optional[str] = None,
    errors: Optional[list[dict[str, Any]]] = None,
) -> dict[str, Any]:
    """Build RFC 7807 problem detail JSON."""
    body = {
        "type": type_uri,
        "title": title,
        "status": status_code,
        "detail": detail,
    }
    if instance:
        body["instance"] = instance
    if trace_id:
        body["traceId"] = trace_id
    if errors:
        body["errors"] = errors
    return body
