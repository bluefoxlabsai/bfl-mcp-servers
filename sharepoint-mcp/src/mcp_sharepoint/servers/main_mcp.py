"""Main MCP server implementation for SharePoint."""

import base64
import logging
import os
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from pydantic import BaseModel, Field

from mcp_sharepoint.sharepoint.client import SharePointClient
from mcp_sharepoint.utils.env import is_env_truthy

logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("SharePoint MCP Server")

# Configure FastMCP settings
settings = mcp.settings
settings.sse_path = "/sse"
settings.streamable_http_path = "/mcp"

# Global client instance
_sharepoint_client: Optional[SharePointClient] = None


def get_sharepoint_client() -> SharePointClient:
    """Get or create SharePoint client instance."""
    global _sharepoint_client
    
    if _sharepoint_client is None:
        site_url = os.getenv("SHAREPOINT_SITE_URL")
        client_id = os.getenv("AZURE_CLIENT_ID")
        client_secret = os.getenv("AZURE_CLIENT_SECRET")
        tenant_id = os.getenv("AZURE_TENANT_ID")
        
        if not all([site_url, client_id, client_secret, tenant_id]):
            raise ValueError(
                "Missing required environment variables: "
                "SHAREPOINT_SITE_URL, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID"
            )
        
        _sharepoint_client = SharePointClient(
            site_url=site_url,
            client_id=client_id,
            client_secret=client_secret,
            tenant_id=tenant_id,
        )
    
    return _sharepoint_client


def is_read_only() -> bool:
    """Check if server is running in read-only mode."""
    return is_env_truthy("READ_ONLY_MODE", "false")


# Tool input models
class SearchContentInput(BaseModel):
    query: str = Field(description="Search query")
    limit: int = Field(default=50, description="Maximum number of results")


class GetFileContentInput(BaseModel):
    file_url: str = Field(description="File URL or server relative URL")


class UploadFileInput(BaseModel):
    library_name: str = Field(description="Document library name")
    file_name: str = Field(description="File name")
    content_base64: str = Field(description="File content encoded in base64")
    folder_path: Optional[str] = Field(default=None, description="Optional folder path")


class CreateFolderInput(BaseModel):
    library_name: str = Field(description="Document library name")
    folder_name: str = Field(description="Folder name")


class GetFilesInLibraryInput(BaseModel):
    library_name: str = Field(description="Document library name")


class GetListItemsInput(BaseModel):
    list_name: str = Field(description="SharePoint list name")
    limit: int = Field(default=100, description="Maximum number of items")


class CreateListItemInput(BaseModel):
    list_name: str = Field(description="SharePoint list name")
    fields: Dict[str, Any] = Field(description="Field values for the new item")


class UpdateListItemInput(BaseModel):
    list_name: str = Field(description="SharePoint list name")
    item_id: int = Field(description="Item ID to update")
    fields: Dict[str, Any] = Field(description="Field values to update")


# SharePoint tools
@mcp.tool()
async def sharepoint_get_site_info() -> Dict[str, Any]:
    """Get information about the SharePoint site."""
    try:
        client = get_sharepoint_client()
        site_info = await client.get_site_info()
        return site_info.model_dump()
    except Exception as e:
        logger.error(f"Error getting site info: {e}")
        return {"error": str(e)}


@mcp.tool()
async def sharepoint_search(input_data: SearchContentInput) -> Dict[str, Any]:
    """Search for content in SharePoint."""
    try:
        client = get_sharepoint_client()
        results = await client.search_content(input_data.query, input_data.limit)
        return {
            "query": input_data.query,
            "results": [result.model_dump() for result in results],
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Error searching content: {e}")
        return {"error": str(e)}


@mcp.tool()
async def sharepoint_get_document_libraries() -> Dict[str, Any]:
    """Get all document libraries in the SharePoint site."""
    try:
        client = get_sharepoint_client()
        libraries = await client.get_document_libraries()
        return {
            "libraries": [library.model_dump() for library in libraries],
            "count": len(libraries)
        }
    except Exception as e:
        logger.error(f"Error getting document libraries: {e}")
        return {"error": str(e)}


@mcp.tool()
async def sharepoint_get_files_in_library(input_data: GetFilesInLibraryInput) -> Dict[str, Any]:
    """Get files in a document library."""
    try:
        client = get_sharepoint_client()
        files = await client.get_files_in_library(input_data.library_name)
        return {
            "library_name": input_data.library_name,
            "files": [file.model_dump() for file in files],
            "count": len(files)
        }
    except Exception as e:
        logger.error(f"Error getting files in library: {e}")
        return {"error": str(e)}


@mcp.tool()
async def sharepoint_get_file_content(input_data: GetFileContentInput) -> Dict[str, Any]:
    """Get content of a SharePoint file."""
    try:
        client = get_sharepoint_client()
        content = await client.get_file_content(input_data.file_url)
        
        # Encode content as base64 for safe transport
        content_base64 = base64.b64encode(content).decode('utf-8')
        
        return {
            "file_url": input_data.file_url,
            "content_base64": content_base64,
            "size": len(content)
        }
    except Exception as e:
        logger.error(f"Error getting file content: {e}")
        return {"error": str(e)}


@mcp.tool()
async def sharepoint_upload_file(input_data: UploadFileInput) -> Dict[str, Any]:
    """Upload a file to SharePoint."""
    if is_read_only():
        return {"error": "Server is running in read-only mode"}
    
    try:
        client = get_sharepoint_client()
        
        # Decode base64 content
        content = base64.b64decode(input_data.content_base64)
        
        uploaded_file = await client.upload_file(
            library_name=input_data.library_name,
            file_name=input_data.file_name,
            content=content,
            folder_path=input_data.folder_path
        )
        
        return {
            "message": "File uploaded successfully",
            "file": uploaded_file.model_dump()
        }
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return {"error": str(e)}


@mcp.tool()
async def sharepoint_create_folder(input_data: CreateFolderInput) -> Dict[str, Any]:
    """Create a folder in a SharePoint document library."""
    if is_read_only():
        return {"error": "Server is running in read-only mode"}
    
    try:
        client = get_sharepoint_client()
        folder = await client.create_folder(
            library_name=input_data.library_name,
            folder_name=input_data.folder_name
        )
        
        return {
            "message": "Folder created successfully",
            "folder": folder.model_dump()
        }
    except Exception as e:
        logger.error(f"Error creating folder: {e}")
        return {"error": str(e)}


@mcp.tool()
async def sharepoint_get_lists() -> Dict[str, Any]:
    """Get all SharePoint lists in the site."""
    try:
        client = get_sharepoint_client()
        lists = await client.get_lists()
        return {
            "lists": [list_item.model_dump() for list_item in lists],
            "count": len(lists)
        }
    except Exception as e:
        logger.error(f"Error getting lists: {e}")
        return {"error": str(e)}


@mcp.tool()
async def sharepoint_get_list_items(input_data: GetListItemsInput) -> Dict[str, Any]:
    """Get items from a SharePoint list."""
    try:
        client = get_sharepoint_client()
        items = await client.get_list_items(input_data.list_name, input_data.limit)
        return {
            "list_name": input_data.list_name,
            "items": [item.model_dump() for item in items],
            "count": len(items)
        }
    except Exception as e:
        logger.error(f"Error getting list items: {e}")
        return {"error": str(e)}


@mcp.tool()
async def sharepoint_create_list_item(input_data: CreateListItemInput) -> Dict[str, Any]:
    """Create a new item in a SharePoint list."""
    if is_read_only():
        return {"error": "Server is running in read-only mode"}
    
    try:
        client = get_sharepoint_client()
        item = await client.create_list_item(
            list_name=input_data.list_name,
            fields=input_data.fields
        )
        
        return {
            "message": "List item created successfully",
            "item": item.model_dump()
        }
    except Exception as e:
        logger.error(f"Error creating list item: {e}")
        return {"error": str(e)}


@mcp.tool()
async def sharepoint_update_list_item(input_data: UpdateListItemInput) -> Dict[str, Any]:
    """Update an existing item in a SharePoint list."""
    if is_read_only():
        return {"error": "Server is running in read-only mode"}
    
    try:
        client = get_sharepoint_client()
        item = await client.update_list_item(
            list_name=input_data.list_name,
            item_id=input_data.item_id,
            fields=input_data.fields
        )
        
        return {
            "message": "List item updated successfully",
            "item": item.model_dump()
        }
    except Exception as e:
        logger.error(f"Error updating list item: {e}")
        return {"error": str(e)}


# Export the FastMCP instance
__all__ = ["mcp"]