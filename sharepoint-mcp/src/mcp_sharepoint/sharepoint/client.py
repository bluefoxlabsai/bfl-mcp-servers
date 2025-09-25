"""SharePoint client implementation."""

import logging
from typing import Any, Dict, List, Optional

import msal
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext

from mcp_sharepoint.models.sharepoint import (
    SharePointFile,
    SharePointFolder,
    SharePointLibrary,
    SharePointList,
    SharePointListItem,
    SharePointSearchResult,
    SharePointSite,
)

logger = logging.getLogger(__name__)


class SharePointClient:
    """SharePoint client for interacting with SharePoint sites."""
    
    def __init__(
        self,
        site_url: str,
        client_id: str,
        client_secret: str,
        tenant_id: str,
    ):
        """Initialize SharePoint client.
        
        Args:
            site_url: SharePoint site URL
            client_id: Azure AD client ID
            client_secret: Azure AD client secret
            tenant_id: Azure AD tenant ID
        """
        self.site_url = site_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self._context: Optional[ClientContext] = None
        
    async def _get_context(self) -> ClientContext:
        """Get authenticated SharePoint context."""
        if self._context is None:
            # Create MSAL app for authentication
            app = msal.ConfidentialClientApplication(
                client_id=self.client_id,
                client_credential=self.client_secret,
                authority=f"https://login.microsoftonline.com/{self.tenant_id}"
            )
            
            # Get access token
            result = app.acquire_token_for_client(
                scopes=[f"{self.site_url}/.default"]
            )
            
            if "access_token" not in result:
                raise Exception(f"Failed to acquire token: {result.get('error_description', 'Unknown error')}")
            
            # Create SharePoint context
            self._context = ClientContext(self.site_url)
            self._context.with_access_token(result["access_token"])
            
        return self._context
    
    async def get_site_info(self) -> SharePointSite:
        """Get information about the SharePoint site."""
        context = await self._get_context()
        web = context.web
        context.load(web)
        context.execute_query()
        
        return SharePointSite(
            id=web.id,
            title=web.title,
            url=web.url,
            description=web.description,
            created=web.created,
            modified=web.last_item_modified_date,
            web_template=web.web_template,
        )
    
    async def search_content(self, query: str, limit: int = 50) -> List[SharePointSearchResult]:
        """Search for content in SharePoint.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of search results
        """
        context = await self._get_context()
        
        # Use SharePoint search API
        search_request = context.search()
        search_request.query_text = query
        search_request.row_limit = limit
        
        results = search_request.execute_query()
        
        search_results = []
        for result in results.primary_query_result.relevant_results:
            search_results.append(SharePointSearchResult(
                title=result.get("Title", ""),
                url=result.get("Path", ""),
                summary=result.get("HitHighlightedSummary", ""),
                author=result.get("Author", ""),
                created=result.get("Created"),
                modified=result.get("LastModifiedTime"),
                file_type=result.get("FileType", ""),
                size=result.get("Size"),
                path=result.get("ServerRedirectedURL", ""),
            ))
        
        return search_results
    
    async def get_document_libraries(self) -> List[SharePointLibrary]:
        """Get all document libraries in the site."""
        context = await self._get_context()
        lists = context.web.lists
        context.load(lists)
        context.execute_query()
        
        libraries = []
        for list_item in lists:
            if list_item.base_template == 101:  # Document Library template
                libraries.append(SharePointLibrary(
                    id=list_item.id,
                    title=list_item.title,
                    description=list_item.description,
                    url=f"{self.site_url}/{list_item.default_view_url}",
                    item_count=list_item.item_count,
                    created=list_item.created,
                    modified=list_item.last_item_modified_date,
                    default_view_url=list_item.default_view_url,
                ))
        
        return libraries
    
    async def get_files_in_library(self, library_name: str) -> List[SharePointFile]:
        """Get files in a document library.
        
        Args:
            library_name: Name of the document library
            
        Returns:
            List of files in the library
        """
        context = await self._get_context()
        library = context.web.lists.get_by_title(library_name)
        items = library.items
        context.load(items)
        context.execute_query()
        
        files = []
        for item in items:
            if item.file_system_object_type == 0:  # File
                file_obj = item.file
                context.load(file_obj)
                context.execute_query()
                
                files.append(SharePointFile(
                    name=file_obj.name,
                    url=f"{self.site_url}{file_obj.server_relative_url}",
                    size=file_obj.length,
                    created=item.created,
                    modified=item.modified,
                    created_by=item.created_by.title if item.created_by else None,
                    modified_by=item.modified_by.title if item.modified_by else None,
                    server_relative_url=file_obj.server_relative_url,
                ))
        
        return files
    
    async def get_file_content(self, file_url: str) -> bytes:
        """Get content of a file.
        
        Args:
            file_url: URL or server relative URL of the file
            
        Returns:
            File content as bytes
        """
        context = await self._get_context()
        
        # Handle both full URLs and server relative URLs
        if file_url.startswith("http"):
            server_relative_url = file_url.replace(self.site_url, "")
        else:
            server_relative_url = file_url
            
        file_obj = context.web.get_file_by_server_relative_url(server_relative_url)
        content = file_obj.read()
        context.execute_query()
        
        return content
    
    async def upload_file(
        self, 
        library_name: str, 
        file_name: str, 
        content: bytes,
        folder_path: Optional[str] = None
    ) -> SharePointFile:
        """Upload a file to SharePoint.
        
        Args:
            library_name: Name of the document library
            file_name: Name of the file to upload
            content: File content as bytes
            folder_path: Optional folder path within the library
            
        Returns:
            Information about the uploaded file
        """
        context = await self._get_context()
        library = context.web.lists.get_by_title(library_name)
        
        if folder_path:
            target_folder = library.root_folder.folders.add(folder_path)
            context.execute_query()
        else:
            target_folder = library.root_folder
        
        uploaded_file = target_folder.upload_file(file_name, content)
        context.execute_query()
        
        return SharePointFile(
            name=uploaded_file.name,
            url=f"{self.site_url}{uploaded_file.server_relative_url}",
            size=len(content),
            server_relative_url=uploaded_file.server_relative_url,
        )
    
    async def create_folder(self, library_name: str, folder_name: str) -> SharePointFolder:
        """Create a folder in a document library.
        
        Args:
            library_name: Name of the document library
            folder_name: Name of the folder to create
            
        Returns:
            Information about the created folder
        """
        context = await self._get_context()
        library = context.web.lists.get_by_title(library_name)
        
        new_folder = library.root_folder.folders.add(folder_name)
        context.execute_query()
        
        return SharePointFolder(
            name=new_folder.name,
            url=f"{self.site_url}{new_folder.server_relative_url}",
            server_relative_url=new_folder.server_relative_url,
        )
    
    async def get_lists(self) -> List[SharePointList]:
        """Get all lists in the site."""
        context = await self._get_context()
        lists = context.web.lists
        context.load(lists)
        context.execute_query()
        
        site_lists = []
        for list_item in lists:
            # Skip system lists and document libraries
            if not list_item.hidden and list_item.base_template != 101:
                site_lists.append(SharePointList(
                    id=list_item.id,
                    title=list_item.title,
                    description=list_item.description,
                    item_count=list_item.item_count,
                    created=list_item.created,
                    modified=list_item.last_item_modified_date,
                    list_type=str(list_item.base_template),
                ))
        
        return site_lists
    
    async def get_list_items(self, list_name: str, limit: int = 100) -> List[SharePointListItem]:
        """Get items from a SharePoint list.
        
        Args:
            list_name: Name of the list
            limit: Maximum number of items to retrieve
            
        Returns:
            List of items
        """
        context = await self._get_context()
        list_obj = context.web.lists.get_by_title(list_name)
        items = list_obj.items.top(limit)
        context.load(items)
        context.execute_query()
        
        list_items = []
        for item in items:
            # Get all field values
            fields = {}
            for field_name, field_value in item.properties.items():
                if not field_name.startswith("_") and field_value is not None:
                    fields[field_name] = field_value
            
            list_items.append(SharePointListItem(
                id=item.id,
                title=item.properties.get("Title"),
                created=item.created,
                modified=item.modified,
                created_by=item.created_by.title if item.created_by else None,
                modified_by=item.modified_by.title if item.modified_by else None,
                fields=fields,
            ))
        
        return list_items
    
    async def create_list_item(self, list_name: str, fields: Dict[str, Any]) -> SharePointListItem:
        """Create a new item in a SharePoint list.
        
        Args:
            list_name: Name of the list
            fields: Field values for the new item
            
        Returns:
            Information about the created item
        """
        context = await self._get_context()
        list_obj = context.web.lists.get_by_title(list_name)
        
        item_create_info = {
            "__metadata": {"type": f"SP.Data.{list_name}ListItem"}
        }
        item_create_info.update(fields)
        
        new_item = list_obj.add_item(item_create_info)
        context.execute_query()
        
        return SharePointListItem(
            id=new_item.id,
            title=new_item.properties.get("Title"),
            created=new_item.created,
            modified=new_item.modified,
            fields=fields,
        )
    
    async def update_list_item(
        self, 
        list_name: str, 
        item_id: int, 
        fields: Dict[str, Any]
    ) -> SharePointListItem:
        """Update an existing item in a SharePoint list.
        
        Args:
            list_name: Name of the list
            item_id: ID of the item to update
            fields: Field values to update
            
        Returns:
            Information about the updated item
        """
        context = await self._get_context()
        list_obj = context.web.lists.get_by_title(list_name)
        item = list_obj.get_item_by_id(item_id)
        
        for field_name, field_value in fields.items():
            item.set_property(field_name, field_value)
        
        item.update()
        context.execute_query()
        
        return SharePointListItem(
            id=item.id,
            title=item.properties.get("Title"),
            created=item.created,
            modified=item.modified,
            fields=fields,
        )