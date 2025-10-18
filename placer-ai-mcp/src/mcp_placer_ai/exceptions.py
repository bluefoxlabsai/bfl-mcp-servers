"""Custom exceptions for Placer.ai MCP Server."""


class PlacerAIError(Exception):
    """Base exception for Placer.ai related errors."""

    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AuthenticationError(PlacerAIError):
    """Raised when API authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, 401)


class RateLimitError(PlacerAIError):
    """Raised when API rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, 429)


class ValidationError(PlacerAIError):
    """Raised when request validation fails."""

    def __init__(self, message: str = "Request validation failed"):
        super().__init__(message, 400)


class NotFoundError(PlacerAIError):
    """Raised when requested resource is not found."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, 404)


class ServiceUnavailableError(PlacerAIError):
    """Raised when Placer.ai service is unavailable."""

    def __init__(self, message: str = "Placer.ai service unavailable"):
        super().__init__(message, 503)