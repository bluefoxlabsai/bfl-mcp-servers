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
async def view_site(url: str, wait_for_selector: str | None = None) -> str:
    """
    View a website and return a summary of its visible text content.

    Args:
        url: The URL to view
        wait_for_selector: Optional CSS selector to wait for before extracting content

    Returns:
        A summary of the visible text content on the page
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            logger.info(f"Viewing site: {url}")

            # Set user agent to avoid bot detection
            await page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            })

            # Navigate to the URL
            await page.goto(url, wait_until="networkidle", timeout=30000)

            # Wait for optional selector if provided
            if wait_for_selector:
                await page.wait_for_selector(wait_for_selector, timeout=10000)

            # Extract visible text content
            content = await page.evaluate("""
                () => {
                    // Remove script and style elements
                    const elements = document.querySelectorAll('script, style');
                    elements.forEach(el => el.remove());

                    // Get text content
                    return document.body ? document.body.innerText : '';
                }
            """)

            # Summarize the content (first 1000 characters)
            summary = content[:1000] + ('...' if len(content) > 1000 else '')
            return f"Summary of {url}:\n" + summary

        except Exception as e:
            error_msg = f"Error viewing {url}: {str(e)}"
            logger.error(error_msg)
            return error_msg

        finally:
            await page.close()
            await browser.close()
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


@main_mcp.tool()
async def take_screenshot(url: str, full_page: bool = False) -> str:
    """
    Take a screenshot of a web page and return a description of what was captured.

    Args:
        url: The URL to take a screenshot of
        full_page: Whether to capture the full page or just the viewport

    Returns:
        A description of the screenshot taken
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            logger.info(f"Taking screenshot of URL: {url}")

            # Set user agent to avoid bot detection
            await page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            })

            # Set viewport size for consistent screenshots
            await page.set_viewport_size({"width": 1280, "height": 720})

            # Navigate to the URL
            await page.goto(url, wait_until="networkidle", timeout=30000)

            # Take screenshot
            screenshot_path = f"/tmp/screenshot_{hash(url)}.png"
            await page.screenshot(path=screenshot_path, full_page=full_page)

            # Get basic page info
            title = await page.title()
            url_final = page.url

            logger.info(f"Successfully took screenshot of {url}")
            return f"Screenshot taken of '{title}' at {url_final}. Image saved as {screenshot_path}. Full page: {full_page}"

        except Exception as e:
            error_msg = f"Error taking screenshot of {url}: {str(e)}"
            logger.error(error_msg)
            return error_msg

        finally:
            await page.close()
            await browser.close()


@main_mcp.tool()
async def get_page_info(url: str) -> str:
    """
    Get comprehensive information about a web page including title, meta description, headings, and links.

    Args:
        url: The URL to analyze

    Returns:
        Structured information about the page
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            logger.info(f"Getting page info for URL: {url}")

            # Set user agent to avoid bot detection
            await page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            })

            # Navigate to the URL
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)

            # Extract comprehensive page information
            page_info = await page.evaluate("""
                () => {
                    const info = {
                        title: document.title,
                        url: window.location.href,
                        metaDescription: '',
                        headings: [],
                        links: [],
                        images: []
                    };

                    // Get meta description
                    const metaDesc = document.querySelector('meta[name="description"]');
                    if (metaDesc) {
                        info.metaDescription = metaDesc.getAttribute('content') || '';
                    }

                    // Get headings
                    ['h1', 'h2', 'h3'].forEach(tag => {
                        const elements = document.querySelectorAll(tag);
                        elements.forEach(el => {
                            info.headings.push({
                                level: tag,
                                text: el.textContent.trim()
                            });
                        });
                    });

                    // Get links (limit to first 20)
                    const linkElements = document.querySelectorAll('a[href]');
                    for (let i = 0; i < Math.min(linkElements.length, 20); i++) {
                        const link = linkElements[i];
                        info.links.push({
                            text: link.textContent.trim(),
                            href: link.href
                        });
                    }

                    // Get images (limit to first 10)
                    const imgElements = document.querySelectorAll('img[src]');
                    for (let i = 0; i < Math.min(imgElements.length, 10); i++) {
                        const img = imgElements[i];
                        info.images.push({
                            src: img.src,
                            alt: img.alt || ''
                        });
                    }

                    return info;
                }
            """)

            logger.info(f"Successfully extracted page info from {url}")
            return f"""
Page Information for: {page_info['url']}

Title: {page_info['title']}

Meta Description: {page_info['metaDescription'] or 'Not found'}

Headings:
{chr(10).join([f"- {h['level'].upper()}: {h['text']}" for h in page_info['headings'][:10]])}

Top Links:
{chr(10).join([f"- {link['text'][:50]}... -> {link['href']}" for link in page_info['links'][:10]])}

Images: {len(page_info['images'])} found
"""

        except Exception as e:
            error_msg = f"Error getting page info for {url}: {str(e)}"
            logger.error(error_msg)
            return error_msg

        finally:
            await page.close()
            await browser.close()