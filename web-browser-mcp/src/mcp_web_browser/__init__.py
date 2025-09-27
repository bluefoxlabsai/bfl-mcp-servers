"""MCP Web Browser Server."""

import asyncio
import logging
import os
import sys
from importlib.metadata import PackageNotFoundError, version

import click
from dotenv import load_dotenv

try:
    __version__ = version("mcp-web-browser")
except PackageNotFoundError:
    # package is not installed
    __version__ = "0.0.0"

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Increase verbosity (can be used multiple times)",
)
@click.option(
    "--env-file",
    type=click.Path(exists=True),
    help="Path to .env file to load",
)
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse", "streamable-http"]),
    default="stdio",
    help="Transport type (stdio, sse, or streamable-http)",
)
@click.option(
    "--port",
    default=8000,
    help="Port to listen on for SSE or Streamable HTTP transport",
)
@click.option(
    "--host",
    default="0.0.0.0",  # noqa: S104
    help="Host to bind to for SSE or Streamable HTTP transport (default: 0.0.0.0)",
)
@click.option(
    "--path",
    default="/mcp",
    help="Path for Streamable HTTP transport (e.g., /mcp).",
)
def main(
    verbose: int,
    env_file: str | None,
    transport: str,
    port: int,
    host: str,
    path: str,
) -> None:
    """Run the MCP Web Browser server."""
    # Setup logging
    logging_level = logging.WARNING
    if verbose == 1:
        logging_level = logging.INFO
    elif verbose >= 2:
        logging_level = logging.DEBUG

    logging.basicConfig(
        level=logging_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    if env_file:
        load_dotenv(env_file, override=True)
    else:
        load_dotenv(override=True)

    # Import here to avoid circular imports
    from mcp_web_browser.server import main_mcp

    final_transport = transport
    final_port = port
    final_host = host
    final_path = path

    run_kwargs = {}
    if final_transport in ["sse", "streamable-http"]:
        run_kwargs.update(
            {
                "transport": final_transport,
                "host": final_host,
                "port": final_port,
            }
        )
        if final_transport == "streamable-http":
            run_kwargs["path"] = final_path

    try:
        logger.info(f"Starting MCP Web Browser server with {final_transport} transport")
        asyncio.run(main_mcp.run_async(**run_kwargs))
    except (KeyboardInterrupt, SystemExit) as e:
        logger.info(f"Server shutdown initiated: {type(e).__name__}")
    except Exception as e:
        logger.error(f"Server encountered an error: {e}", exc_info=True)
        sys.exit(1)


__all__ = ["main", "__version__"]

if __name__ == "__main__":
    main()