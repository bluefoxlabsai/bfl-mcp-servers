"""Custom exceptions for SharePoint MCP."""


class SharePointMCPError(Exception):
    """Base exception for SharePoint MCP errors."""
    pass


class AuthenticationError(SharePointMCPError):
    """Raised when authentication fails."""
    pass


class SharePointConnectionError(SharePointMCPError):
    """Raised when connection to SharePoint fails."""
    pass


class SharePointPermissionError(SharePointMCPError):
    """Raised when insufficient permissions for SharePoint operation."""
    pass


class SharePointNotFoundError(SharePointMCPError):
    """Raised when SharePoint resource is not found."""
    pass