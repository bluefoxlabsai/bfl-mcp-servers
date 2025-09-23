"""
Enhanced Google Search MCP Server

A comprehensive FastMCP server that provides full Google Custom Search API functionality.
This server exposes multiple tools for different types of searches and advanced search features.
Requires Google API Key and Custom Search Engine ID stored in environment variables.
"""

import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Load configuration from .env
load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY') or os.getenv('GOOGLE_SEARCH_API_KEY')
GOOGLE_CSE_ID = os.getenv('GOOGLE_CSE_ID')

# Initialize FastMCP server
mcp = FastMCP("GoogleSearchAPI")


def _build_search_service():
    """Initialize and return Google Custom Search API service."""
    if not GOOGLE_API_KEY:
        raise ValueError("Google API Key not found. Set GOOGLE_API_KEY or GOOGLE_SEARCH_API_KEY environment variable.")
    if not GOOGLE_CSE_ID:
        raise ValueError("Google CSE ID not found. Set GOOGLE_CSE_ID environment variable.")
    
    return build("customsearch", "v1", developerKey=GOOGLE_API_KEY)


def _format_search_results(result: Dict[str, Any]) -> Dict[str, Any]:
    """Format Google Search API results into a consistent structure."""
    formatted_results = []
    
    if "items" in result:
        for item in result["items"]:
            formatted_item = {
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "display_link": item.get("displayLink", ""),
                "formatted_url": item.get("formattedUrl", ""),
            }
            
            # Add image data if available
            if "pagemap" in item:
                pagemap = item["pagemap"]
                if "cse_image" in pagemap:
                    formatted_item["image"] = pagemap["cse_image"][0].get("src", "")
                if "metatags" in pagemap and pagemap["metatags"]:
                    meta = pagemap["metatags"][0]
                    formatted_item["meta_description"] = meta.get("og:description", meta.get("description", ""))
                    formatted_item["meta_image"] = meta.get("og:image", "")
            
            formatted_results.append(formatted_item)
    
    search_info = result.get("searchInformation", {})
    
    return {
        "success": True,
        "results": formatted_results,
        "total_results": search_info.get("totalResults", "0"),
        "search_time": search_info.get("searchTime", 0),
        "formatted_total_results": search_info.get("formattedTotalResults", "0"),
        "formatted_search_time": search_info.get("formattedSearchTime", "0"),
    }


@mcp.tool()
async def search_google(
    query: str, 
    num_results: int = 10,
    start_index: int = 1,
    language: str = "en",
    country: str = "us"
) -> Dict[str, Any]:
    """
    Perform a comprehensive Google search with advanced options.
    
    Args:
        query (str): The search query string
        num_results (int): Number of results to return (1-10, default: 10)
        start_index (int): Starting index for results (default: 1)
        language (str): Language code for results (default: "en")
        country (str): Country code for results (default: "us")
        
    Returns:
        Dict[str, Any]: Search results with metadata
    """
    try:
        service = _build_search_service()
        
        # Execute the search
        result = service.cse().list(
            q=query,
            cx=GOOGLE_CSE_ID,
            num=min(num_results, 10),  # API limit is 10
            start=start_index,
            lr=f"lang_{language}",
            gl=country
        ).execute()
        
        return _format_search_results(result)
        
    except HttpError as error:
        return {
            "success": False,
            "error": f"Google API Error: {str(error)}",
            "results": []
        }
    except Exception as error:
        return {
            "success": False,
            "error": f"Unexpected error: {str(error)}",
            "results": []
        }


@mcp.tool()
async def search_images(
    query: str,
    num_results: int = 10,
    image_size: str = "large",
    image_type: str = "photo",
    safe_search: str = "active"
) -> Dict[str, Any]:
    """
    Search for images using Google Custom Search.
    
    Args:
        query (str): The image search query
        num_results (int): Number of results to return (1-10, default: 10)
        image_size (str): Image size filter ("huge", "icon", "large", "medium", "small", "xlarge", "xxlarge")
        image_type (str): Image type filter ("clipart", "face", "lineart", "stock", "photo", "animated")
        safe_search (str): Safe search setting ("active", "off")
        
    Returns:
        Dict[str, Any]: Image search results with metadata
    """
    try:
        service = _build_search_service()
        
        result = service.cse().list(
            q=query,
            cx=GOOGLE_CSE_ID,
            num=min(num_results, 10),
            searchType="image",
            imgSize=image_size,
            imgType=image_type,
            safe=safe_search
        ).execute()
        
        formatted_result = _format_search_results(result)
        
        # Add image-specific metadata
        if formatted_result["success"] and "items" in result:
            for i, item in enumerate(result["items"]):
                if i < len(formatted_result["results"]):
                    image_data = item.get("image", {})
                    formatted_result["results"][i].update({
                        "image_url": item.get("link", ""),
                        "thumbnail_url": image_data.get("thumbnailLink", ""),
                        "image_width": image_data.get("width", 0),
                        "image_height": image_data.get("height", 0),
                        "thumbnail_width": image_data.get("thumbnailWidth", 0),
                        "thumbnail_height": image_data.get("thumbnailHeight", 0),
                        "context_link": image_data.get("contextLink", ""),
                    })
        
        return formatted_result
        
    except HttpError as error:
        return {
            "success": False,
            "error": f"Google API Error: {str(error)}",
            "results": []
        }
    except Exception as error:
        return {
            "success": False,
            "error": f"Unexpected error: {str(error)}",
            "results": []
        }


@mcp.tool()
async def search_by_date_range(
    query: str,
    start_date: str,
    end_date: str,
    num_results: int = 10,
    sort_by: str = "date"
) -> Dict[str, Any]:
    """
    Search Google with date range filtering.
    
    Args:
        query (str): The search query
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        num_results (int): Number of results to return (1-10, default: 10)
        sort_by (str): Sort order ("date" or "relevance")
        
    Returns:
        Dict[str, Any]: Date-filtered search results
    """
    try:
        service = _build_search_service()
        
        # Format date range for Google API
        date_restrict = f"date:r:{start_date}:{end_date}"
        
        result = service.cse().list(
            q=query,
            cx=GOOGLE_CSE_ID,
            num=min(num_results, 10),
            dateRestrict=date_restrict,
            sort=f"date:r:{start_date}:{end_date}" if sort_by == "date" else None
        ).execute()
        
        return _format_search_results(result)
        
    except HttpError as error:
        return {
            "success": False,
            "error": f"Google API Error: {str(error)}",
            "results": []
        }
    except Exception as error:
        return {
            "success": False,
            "error": f"Unexpected error: {str(error)}",
            "results": []
        }


@mcp.tool()
async def search_site_specific(
    query: str,
    site: str,
    num_results: int = 10,
    exclude_sites: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Search within specific sites or exclude specific sites.
    
    Args:
        query (str): The search query
        site (str): Site to search within (e.g., "reddit.com", "github.com")
        num_results (int): Number of results to return (1-10, default: 10)
        exclude_sites (List[str], optional): List of sites to exclude from results
        
    Returns:
        Dict[str, Any]: Site-specific search results
    """
    try:
        service = _build_search_service()
        
        # Build the search query with site restrictions
        modified_query = f"site:{site} {query}"
        
        if exclude_sites:
            for exclude_site in exclude_sites:
                modified_query += f" -site:{exclude_site}"
        
        result = service.cse().list(
            q=modified_query,
            cx=GOOGLE_CSE_ID,
            num=min(num_results, 10)
        ).execute()
        
        return _format_search_results(result)
        
    except HttpError as error:
        return {
            "success": False,
            "error": f"Google API Error: {str(error)}",
            "results": []
        }
    except Exception as error:
        return {
            "success": False,
            "error": f"Unexpected error: {str(error)}",
            "results": []
        }


@mcp.tool()
async def search_file_type(
    query: str,
    file_type: str,
    num_results: int = 10,
    exact_terms: Optional[str] = None,
    exclude_terms: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search for specific file types with advanced query options.
    
    Args:
        query (str): The search query
        file_type (str): File type to search for (e.g., "pdf", "doc", "xls", "ppt")
        num_results (int): Number of results to return (1-10, default: 10)
        exact_terms (str, optional): Exact phrase that must be in results
        exclude_terms (str, optional): Terms to exclude from results
        
    Returns:
        Dict[str, Any]: File type specific search results
    """
    try:
        service = _build_search_service()
        
        # Build query with file type
        modified_query = f"filetype:{file_type} {query}"
        
        if exact_terms:
            modified_query += f' "{exact_terms}"'
        
        if exclude_terms:
            for term in exclude_terms.split():
                modified_query += f" -{term}"
        
        result = service.cse().list(
            q=modified_query,
            cx=GOOGLE_CSE_ID,
            num=min(num_results, 10)
        ).execute()
        
        return _format_search_results(result)
        
    except HttpError as error:
        return {
            "success": False,
            "error": f"Google API Error: {str(error)}",
            "results": []
        }
    except Exception as error:
        return {
            "success": False,
            "error": f"Unexpected error: {str(error)}",
            "results": []
        }


@mcp.tool()
async def search_related(
    url: str,
    num_results: int = 10
) -> Dict[str, Any]:
    """
    Find pages related to a specific URL.
    
    Args:
        url (str): The URL to find related pages for
        num_results (int): Number of results to return (1-10, default: 10)
        
    Returns:
        Dict[str, Any]: Related pages search results
    """
    try:
        service = _build_search_service()
        
        result = service.cse().list(
            q=f"related:{url}",
            cx=GOOGLE_CSE_ID,
            num=min(num_results, 10)
        ).execute()
        
        return _format_search_results(result)
        
    except HttpError as error:
        return {
            "success": False,
            "error": f"Google API Error: {str(error)}",
            "results": []
        }
    except Exception as error:
        return {
            "success": False,
            "error": f"Unexpected error: {str(error)}",
            "results": []
        }


@mcp.tool()
async def search_cached(
    url: str
) -> Dict[str, Any]:
    """
    Get the cached version of a specific URL from Google.
    
    Args:
        url (str): The URL to get cached version for
        
    Returns:
        Dict[str, Any]: Cached page information
    """
    try:
        service = _build_search_service()
        
        result = service.cse().list(
            q=f"cache:{url}",
            cx=GOOGLE_CSE_ID,
            num=1
        ).execute()
        
        return _format_search_results(result)
        
    except HttpError as error:
        return {
            "success": False,
            "error": f"Google API Error: {str(error)}",
            "results": []
        }
    except Exception as error:
        return {
            "success": False,
            "error": f"Unexpected error: {str(error)}",
            "results": []
        }


@mcp.tool()
async def get_search_suggestions(
    query: str,
    max_suggestions: int = 10
) -> Dict[str, Any]:
    """
    Get search suggestions for a given query.
    Note: This uses a basic implementation as Google doesn't provide 
    suggestion API in Custom Search API.
    
    Args:
        query (str): The query to get suggestions for
        max_suggestions (int): Maximum number of suggestions to return
        
    Returns:
        Dict[str, Any]: Search suggestions
    """
    try:
        # Perform a search and extract related terms
        service = _build_search_service()
        
        result = service.cse().list(
            q=query,
            cx=GOOGLE_CSE_ID,
            num=5
        ).execute()
        
        suggestions = []
        if "items" in result:
            for item in result["items"]:
                title_words = item.get("title", "").lower().split()
                snippet_words = item.get("snippet", "").lower().split()
                
                # Extract potential related terms
                for word in title_words + snippet_words:
                    if len(word) > 3 and word.isalpha() and word not in suggestions:
                        suggestions.append(word)
                        if len(suggestions) >= max_suggestions:
                            break
                
                if len(suggestions) >= max_suggestions:
                    break
        
        return {
            "success": True,
            "query": query,
            "suggestions": suggestions[:max_suggestions]
        }
        
    except Exception as error:
        return {
            "success": False,
            "error": f"Error generating suggestions: {str(error)}",
            "suggestions": []
        }


@mcp.tool()
async def get_api_status() -> Dict[str, Any]:
    """
    Check the status of the Google Search API configuration and quota.
    
    Returns:
        Dict[str, Any]: API status information
    """
    try:
        # Check if API key and CSE ID are configured
        if not GOOGLE_API_KEY:
            return {
                "status": "error",
                "message": "Google API Key not configured",
                "configured": False
            }
        
        if not GOOGLE_CSE_ID:
            return {
                "status": "error",
                "message": "Google CSE ID not configured",
                "configured": False
            }
        
        # Test API with a simple search
        service = _build_search_service()
        result = service.cse().list(
            q="test",
            cx=GOOGLE_CSE_ID,
            num=1
        ).execute()
        
        return {
            "status": "active",
            "message": "Google Search API is working correctly",
            "configured": True,
            "api_key_length": len(GOOGLE_API_KEY),
            "cse_id_configured": bool(GOOGLE_CSE_ID),
            "test_search_successful": True,
            "quota_available": True  # If we get here, quota is available
        }
        
    except HttpError as error:
        error_details = str(error)
        if "quotaExceeded" in error_details:
            return {
                "status": "quota_exceeded",
                "message": "Google Search API quota exceeded",
                "configured": True,
                "quota_available": False
            }
        else:
            return {
                "status": "error",
                "message": f"Google API Error: {error_details}",
                "configured": True
            }
    
    except Exception as error:
        return {
            "status": "error",
            "message": f"Configuration error: {str(error)}",
            "configured": False
        }


# Add resource for API documentation
@mcp.resource("docs://google-search-api-docs")
async def get_api_docs() -> str:
    """
    Get comprehensive documentation for the Google Search MCP Server.
    
    Returns:
        str: Markdown documentation
    """
    return """
# Google Search MCP Server Documentation

## Overview
This server provides comprehensive access to Google Custom Search API functionality through FastMCP.

## Available Tools

### 1. search_google
Perform a comprehensive Google search with advanced options.
- **query**: Search query string
- **num_results**: Number of results (1-10, default: 10)
- **start_index**: Starting index for pagination (default: 1)
- **language**: Language code (default: "en")
- **country**: Country code (default: "us")

### 2. search_images
Search for images using Google Custom Search.
- **query**: Image search query
- **num_results**: Number of results (1-10, default: 10)
- **image_size**: Size filter (huge, icon, large, medium, small, xlarge, xxlarge)
- **image_type**: Type filter (clipart, face, lineart, stock, photo, animated)
- **safe_search**: Safe search setting (active, off)

### 3. search_by_date_range
Search with date range filtering.
- **query**: Search query
- **start_date**: Start date (YYYY-MM-DD format)
- **end_date**: End date (YYYY-MM-DD format)
- **num_results**: Number of results (1-10, default: 10)
- **sort_by**: Sort order (date or relevance)

### 4. search_site_specific
Search within specific sites or exclude sites.
- **query**: Search query
- **site**: Site to search within (e.g., "reddit.com")
- **num_results**: Number of results (1-10, default: 10)
- **exclude_sites**: List of sites to exclude

### 5. search_file_type
Search for specific file types.
- **query**: Search query
- **file_type**: File type (pdf, doc, xls, ppt, etc.)
- **num_results**: Number of results (1-10, default: 10)
- **exact_terms**: Exact phrase to include
- **exclude_terms**: Terms to exclude

### 6. search_related
Find pages related to a specific URL.
- **url**: URL to find related pages for
- **num_results**: Number of results (1-10, default: 10)

### 7. search_cached
Get cached version of a URL from Google.
- **url**: URL to get cached version for

### 8. get_search_suggestions
Get search suggestions for a query.
- **query**: Query to get suggestions for
- **max_suggestions**: Maximum suggestions to return

### 9. get_api_status
Check API configuration and quota status.

## Configuration
Set these environment variables:
- `GOOGLE_API_KEY` or `GOOGLE_SEARCH_API_KEY`: Your Google API key
- `GOOGLE_CSE_ID`: Your Custom Search Engine ID

## Usage Examples

### Basic search:
```python
result = await search_google("artificial intelligence")
```

### Image search:
```python
result = await search_images("cats", image_size="large", image_type="photo")
```

### Site-specific search:
```python
result = await search_site_specific("machine learning", "github.com")
```

### File type search:
```python
result = await search_file_type("research paper", "pdf")
```

## Response Format
All search functions return:
```json
{
  "success": boolean,
  "results": [
    {
      "title": "Page title",
      "link": "URL",
      "snippet": "Description",
      "display_link": "Display URL",
      "formatted_url": "Formatted URL",
      "meta_description": "Meta description",
      "meta_image": "Meta image URL"
    }
  ],
  "total_results": "Total count",
  "search_time": 0.123,
  "error": "Error message (if any)"
}
```
"""


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Google Search MCP Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--transport", default="sse", choices=["sse", "streamable-http", "stdio"], 
                       help="Transport protocol")
    
    args = parser.parse_args()
    
    print(f"🚀 Starting Enhanced Google Search MCP Server")
    print(f"📡 Transport: {args.transport}")
    print(f"🌐 Server: http://{args.host}:{args.port}")
    print(f"🔑 API Key configured: {'✅' if GOOGLE_API_KEY else '❌'}")
    print(f"🔍 CSE ID configured: {'✅' if GOOGLE_CSE_ID else '❌'}")
    
    if args.transport == "stdio":
        print("📟 Starting in STDIO mode...")
        mcp.run()
    else:
        print("🌐 Starting HTTP server with SSE transport...")
        # Use uvicorn for HTTP transports with FastMCP app methods
        import uvicorn
        if args.transport == "sse":
            app = mcp.sse_app()
        else:  # streamable-http
            app = mcp.streamable_http_app()
        
        print(f"Starting uvicorn with host={args.host}, port={args.port}")
        uvicorn.run(app, host=args.host, port=args.port)