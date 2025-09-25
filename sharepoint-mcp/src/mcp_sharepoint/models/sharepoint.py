"""SharePoint data models."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SharePointFile(BaseModel):
    """Represents a SharePoint file."""
    
    name: str = Field(description="File name")
    url: str = Field(description="File URL")
    size: Optional[int] = Field(default=None, description="File size in bytes")
    created: Optional[datetime] = Field(default=None, description="Creation date")
    modified: Optional[datetime] = Field(default=None, description="Last modified date")
    created_by: Optional[str] = Field(default=None, description="Created by user")
    modified_by: Optional[str] = Field(default=None, description="Last modified by user")
    content_type: Optional[str] = Field(default=None, description="MIME content type")
    server_relative_url: Optional[str] = Field(default=None, description="Server relative URL")


class SharePointFolder(BaseModel):
    """Represents a SharePoint folder."""
    
    name: str = Field(description="Folder name")
    url: str = Field(description="Folder URL")
    created: Optional[datetime] = Field(default=None, description="Creation date")
    modified: Optional[datetime] = Field(default=None, description="Last modified date")
    item_count: Optional[int] = Field(default=None, description="Number of items in folder")
    server_relative_url: Optional[str] = Field(default=None, description="Server relative URL")


class SharePointListItem(BaseModel):
    """Represents a SharePoint list item."""
    
    id: int = Field(description="Item ID")
    title: Optional[str] = Field(default=None, description="Item title")
    created: Optional[datetime] = Field(default=None, description="Creation date")
    modified: Optional[datetime] = Field(default=None, description="Last modified date")
    created_by: Optional[str] = Field(default=None, description="Created by user")
    modified_by: Optional[str] = Field(default=None, description="Last modified by user")
    fields: Dict[str, Any] = Field(default_factory=dict, description="Custom fields")


class SharePointList(BaseModel):
    """Represents a SharePoint list."""
    
    id: str = Field(description="List ID")
    title: str = Field(description="List title")
    description: Optional[str] = Field(default=None, description="List description")
    item_count: Optional[int] = Field(default=None, description="Number of items")
    created: Optional[datetime] = Field(default=None, description="Creation date")
    modified: Optional[datetime] = Field(default=None, description="Last modified date")
    list_type: Optional[str] = Field(default=None, description="List type")


class SharePointSite(BaseModel):
    """Represents a SharePoint site."""
    
    id: str = Field(description="Site ID")
    title: str = Field(description="Site title")
    url: str = Field(description="Site URL")
    description: Optional[str] = Field(default=None, description="Site description")
    created: Optional[datetime] = Field(default=None, description="Creation date")
    modified: Optional[datetime] = Field(default=None, description="Last modified date")
    web_template: Optional[str] = Field(default=None, description="Web template")


class SharePointSearchResult(BaseModel):
    """Represents a SharePoint search result."""
    
    title: str = Field(description="Result title")
    url: str = Field(description="Result URL")
    summary: Optional[str] = Field(default=None, description="Result summary")
    author: Optional[str] = Field(default=None, description="Content author")
    created: Optional[datetime] = Field(default=None, description="Creation date")
    modified: Optional[datetime] = Field(default=None, description="Last modified date")
    file_type: Optional[str] = Field(default=None, description="File type")
    size: Optional[int] = Field(default=None, description="File size")
    path: Optional[str] = Field(default=None, description="File path")


class SharePointLibrary(BaseModel):
    """Represents a SharePoint document library."""
    
    id: str = Field(description="Library ID")
    title: str = Field(description="Library title")
    description: Optional[str] = Field(default=None, description="Library description")
    url: str = Field(description="Library URL")
    item_count: Optional[int] = Field(default=None, description="Number of items")
    created: Optional[datetime] = Field(default=None, description="Creation date")
    modified: Optional[datetime] = Field(default=None, description="Last modified date")
    default_view_url: Optional[str] = Field(default=None, description="Default view URL")