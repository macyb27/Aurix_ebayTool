"""Custom Exceptions für AURIX Backend."""


class AurixError(Exception):
    """Basis-Exception für AURIX."""

    pass


class EbayApiError(AurixError):
    """eBay API Fehler."""

    def __init__(self, message: str, status_code: int | None = None, response: str | None = None):
        self.status_code = status_code
        self.response = response
        super().__init__(message)


class EbayTokenError(AurixError):
    """eBay Token Fehler (abgelaufen, ungültig)."""

    pass


class EbayRateLimitError(EbayApiError):
    """eBay Rate Limit (429)."""

    pass


class VisionServiceError(AurixError):
    """Vision/AI Service Fehler."""

    pass


class ValidationError(AurixError):
    """Validierungsfehler."""

    pass
