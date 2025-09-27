"""MCP Web Browser Server implementation."""

import asyncio
import logging
from typing import Any

from fastmcp import FastMCP
from playwright.async_api import async_playwright
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

# Create the FastMCP app
main_mcp = FastMCP(
    "Web Browser",
    description="A Model Context Protocol server for web browsing using headless browser technology.",
)


async def health_check(request: Request) -> JSONResponse:
    """Health check endpoint for Kubernetes probes."""
    return JSONResponse({"status": "ok"})


@main_mcp.custom_route("/health", methods=["GET"], include_in_schema=False)
async def _health_check_route(request: Request) -> JSONResponse:
    return await health_check(request)


@main_mcp.tool()
async def browse_url(url: str, wait_for_selector: str | None = None) -> str:
    """
    Browse to a URL and return the page content.

    Args:
        url: The URL to browse to
        wait_for_selector: Optional CSS selector to wait for before extracting content

    Returns:
        The text content of the page
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            logger.info(f"Browsing to URL: {url}")

            # Set user agent to avoid bot detection
            await page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            })

            # Navigate to the URL
            await page.goto(url, wait_until="networkidle", timeout=30000)

            # Wait for optional selector if provided
            if wait_for_selector:
                await page.wait_for_selector(wait_for_selector, timeout=10000)

            # Extract text content
            content = await page.evaluate("""
                () => {
                    // Remove script and style elements
                    const elements = document.querySelectorAll('script, style');
                    elements.forEach(el => el.remove());

                    // Get text content
                    return document.body ? document.body.innerText : '';
                }
            """)

            logger.info(f"Successfully extracted content from {url}")
            return str(content)

        except Exception as e:
            error_msg = f"Error browsing {url}: {str(e)}"
            logger.error(error_msg)
            return error_msg

        finally:
            await page.close()
            await browser.close()


@main_mcp.tool()
async def get_page_title(url: str) -> str:
    """
    Get the title of a web page.

    Args:
        url: The URL to get the title from

    Returns:
        The page title
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            logger.info(f"Getting title from URL: {url}")

            await page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            })

            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            title = await page.title()

            logger.info(f"Successfully got title from {url}: {title}")
            return str(title)

        except Exception as e:
            error_msg = f"Error getting title from {url}: {str(e)}"
            logger.error(error_msg)
            return error_msg

        finally:
            await page.close()
            await browser.close()