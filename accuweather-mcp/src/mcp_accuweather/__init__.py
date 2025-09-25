"""AccuWeather MCP Server - FastMCP implementation for weather data."""

import asyncio
import sys
from typing import Optional

import click

from .server import create_server


def main() -> None:
    """Main entry point for the AccuWeather MCP server."""
    
    @click.command()
    @click.option("--port", type=int, help="Start the server with SSE transport on the specified port")
    @click.option("--help", is_flag=True, help="Show this help message")
    def cli(port: Optional[int] = None, help: bool = False) -> None:
        """AccuWeather MCP Server - FastMCP implementation."""
        
        if help:
            print("""
Usage: mcp-accuweather [options]

Options:
  --port <number>    Start the server with SSE transport on the specified port
  --help             Show this help message

Examples:
  mcp-accuweather                  # Start with stdio transport (default)
  mcp-accuweather --port 8000      # Start with SSE transport on port 8000

Environment Variables:
  ACCUWEATHER_API_KEY             # Required: Your AccuWeather API key
  ACCUWEATHER_BASE_URL            # Optional: API base URL (default: http://dataservice.accuweather.com)
            """)
            return
        
        server = create_server()
        
        if port:
            # SSE server mode
            print(f"Starting AccuWeather MCP Server with SSE transport on port {port}")
            print(f"SSE endpoint available at: http://0.0.0.0:{port}/sse")
            
            # Use FastMCP's built-in SSE async runner
            asyncio.run(server.run_sse_async(host="0.0.0.0", port=port))
        else:
            # STDIO mode (default)
            print("Starting AccuWeather MCP Server in STDIO mode", file=sys.stderr)
            server.run()
    
    cli()


if __name__ == "__main__":
    main()