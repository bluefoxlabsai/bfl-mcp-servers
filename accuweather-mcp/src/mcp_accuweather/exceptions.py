"""Custom exceptions for AccuWeather MCP server."""


class AccuWeatherError(Exception):
    """Base exception for AccuWeather API errors."""
    pass


class AuthenticationError(AccuWeatherError):
    """Exception raised for authentication errors."""
    pass


class RateLimitError(AccuWeatherError):
    """Exception raised when API rate limit is exceeded."""
    pass


class LocationNotFoundError(AccuWeatherError):
    """Exception raised when a location is not found."""
    pass


class InvalidParameterError(AccuWeatherError):
    """Exception raised for invalid parameters."""
    pass