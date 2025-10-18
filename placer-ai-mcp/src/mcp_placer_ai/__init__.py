"""Placer.ai MCP Server - Location Analytics for AI."""

__version__ = "0.1.0"

def main():
    """Main entry point for the MCP server."""
    from .server import main as server_main
    server_main()

if __name__ == "__main__":
    main()

from .server import create_server

__all__ = ["create_server"]