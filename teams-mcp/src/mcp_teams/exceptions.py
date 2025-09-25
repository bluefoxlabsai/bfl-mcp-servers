"""Custom exceptions for Teams MCP."""


class TeamsMCPError(Exception):
    """Base exception for Teams MCP errors."""
    pass


class AuthenticationError(TeamsMCPError):
    """Raised when authentication fails."""
    pass


class TeamsConnectionError(TeamsMCPError):
    """Raised when connection to Teams fails."""
    pass


class TeamsPermissionError(TeamsMCPError):
    """Raised when insufficient permissions for Teams operation."""
    pass


class TeamsNotFoundError(TeamsMCPError):
    """Raised when Teams resource is not found."""
    pass