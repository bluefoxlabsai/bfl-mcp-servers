# Enhanced Google Search MCP Server

A comprehensive FastMCP server that provides full Google Custom Search API functionality with advanced search capabilities.

## 🌟 Features

### Core Search Functions
- **🔍 Basic Web Search**: Standard Google search with language and country filters
- **🖼️ Image Search**: Dedicated image search with size, type, and safety filters
- **📅 Date Range Search**: Search within specific date ranges
- **🌐 Site-Specific Search**: Search within or exclude specific websites
- **📄 File Type Search**: Search for specific file types (PDF, DOC, XLS, etc.)
- **🔗 Related Pages**: Find pages related to a specific URL
- **💾 Cached Pages**: Access Google's cached version of pages
- **💡 Search Suggestions**: Get related search terms
- **📊 API Status**: Monitor API health and quota usage

### Advanced Features
- **Rich Metadata**: Includes thumbnails, meta tags, and structured data
- **Flexible Pagination**: Support for result pagination and custom start indices
- **Error Handling**: Comprehensive error handling with detailed error messages
- **Quota Management**: Built-in quota monitoring and status reporting
- **Documentation**: Self-documenting with built-in API documentation

## 🚀 Quick Start

### Prerequisites
1. **Google API Key**: Get from [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. **Custom Search Engine ID**: Create at [Google CSE](https://cse.google.com/cse/)

### Installation

1. **Clone and setup**:
```bash
cd google-search-mcp
cp .env.example .env
```

2. **Configure environment variables**:
```bash
# Edit .env file
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CSE_ID=your_custom_search_engine_id_here
```

3. **Install dependencies**:
```bash
uv sync
```

4. **Run the enhanced server**:
```bash
uv run enhanced_google_search_server.py
```

## 🛠️ API Documentation

### 1. Basic Web Search
```python
await search_google(
    query="artificial intelligence",
    num_results=10,
    start_index=1,
    language="en",
    country="us"
)
```

### 2. Image Search
```python
await search_images(
    query="sunset landscape",
    num_results=10,
    image_size="large",
    image_type="photo",
    safe_search="active"
)
```

### 3. Date Range Search
```python
await search_by_date_range(
    query="technology news",
    start_date="2024-01-01",
    end_date="2024-12-31",
    num_results=10,
    sort_by="date"
)
```

### 4. Site-Specific Search
```python
await search_site_specific(
    query="machine learning tutorials",
    site="github.com",
    num_results=10,
    exclude_sites=["spam-site.com"]
)
```

### 5. File Type Search
```python
await search_file_type(
    query="research paper machine learning",
    file_type="pdf",
    num_results=10,
    exact_terms="neural networks",
    exclude_terms="advertisement"
)
```

### 6. Related Pages
```python
await search_related(
    url="https://example.com",
    num_results=10
)
```

### 7. Cached Pages
```python
await search_cached(
    url="https://example.com"
)
```

### 8. Search Suggestions
```python
await get_search_suggestions(
    query="machine learn",
    max_suggestions=10
)
```

### 9. API Status Check
```python
await get_api_status()
```

## 📊 Response Format

All search functions return structured data:

```json
{
  "success": true,
  "results": [
    {
      "title": "Page Title",
      "link": "https://example.com",
      "snippet": "Page description snippet",
      "display_link": "example.com",
      "formatted_url": "https://example.com/page",
      "meta_description": "Meta description",
      "meta_image": "https://example.com/image.jpg",
      "image_url": "https://example.com/image.jpg", // For image searches
      "thumbnail_url": "https://example.com/thumb.jpg", // For image searches
      "image_width": 1920, // For image searches
      "image_height": 1080 // For image searches
    }
  ],
  "total_results": "1,234,567",
  "search_time": 0.123,
  "formatted_total_results": "About 1,234,567 results",
  "formatted_search_time": "0.12 seconds"
}
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Google API key from Cloud Console | ✅ |
| `GOOGLE_CSE_ID` | Custom Search Engine ID | ✅ |

### Image Search Options

#### Image Sizes
- `huge`: Very large images
- `icon`: Icon-sized images
- `large`: Large images (default)
- `medium`: Medium-sized images
- `small`: Small images
- `xlarge`: Extra large images
- `xxlarge`: Extra extra large images

#### Image Types
- `clipart`: Clipart images
- `face`: Face images
- `lineart`: Line art images
- `stock`: Stock photos
- `photo`: Photographs (default)
- `animated`: Animated images

#### Safe Search
- `active`: Enable safe search (default)
- `off`: Disable safe search

## 🐳 Docker Deployment

Use the existing Dockerfile or create a new one for the enhanced server:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen

COPY . .

ENV GOOGLE_API_KEY=""
ENV GOOGLE_CSE_ID=""

EXPOSE 8000

CMD ["uv", "run", "enhanced_google_search_server.py", "--host", "0.0.0.0", "--port", "8000"]
```

## ☸️ Kubernetes Deployment

The enhanced server can be deployed using the same Helm chart as the basic server. Update the image command:

```yaml
# In values.yaml
image:
  repository: bfljerum/enhanced-google-search-mcp
  tag: "latest"

# Override the startup command
container:
  command: ["uv", "run", "enhanced_google_search_server.py"]
  args: ["--host", "0.0.0.0", "--port", "8000"]
```

## 🔗 LibreChat Integration

Add to your LibreChat configuration:

```yaml
mcpServers:
  enhanced-google-search:
    type: streamable-http
    url: 'http://enhanced-google-search-mcp.default.svc.cluster.local:8000'
    timeout: 30000
    startup: true
    chatMenu: true
    serverInstructions: |
      You are an enhanced Google Search assistant with comprehensive search capabilities.
      You can perform:
      - Basic web searches with language/country filters
      - Image searches with size and type filters
      - Date range searches for recent content
      - Site-specific searches (within or excluding sites)
      - File type searches (PDF, DOC, XLS, etc.)
      - Related page discovery
      - Cached page access
      - Search suggestions
      
      Always provide clear, relevant results and cite your sources.
      Use the most appropriate search function for each user request.
```

## 🔍 Advanced Search Examples

### Academic Research
```python
# Search for recent research papers
await search_file_type(
    query="artificial intelligence ethics",
    file_type="pdf",
    exact_terms="research paper"
)

# Search within academic sites
await search_site_specific(
    query="machine learning algorithms",
    site="arxiv.org"
)
```

### News and Current Events
```python
# Search for recent news
await search_by_date_range(
    query="technology breakthrough",
    start_date="2024-11-01",
    end_date="2024-11-30",
    sort_by="date"
)
```

### Technical Documentation
```python
# Find API documentation
await search_site_specific(
    query="REST API documentation",
    site="github.com",
    exclude_sites=["spam-docs.com"]
)
```

### Visual Content
```python
# Find high-quality images
await search_images(
    query="data visualization examples",
    image_size="large",
    image_type="photo",
    safe_search="active"
)
```

## 📈 Monitoring and Limits

### API Quotas
- **Free Tier**: 100 searches per day
- **Paid Tier**: Up to 10,000 searches per day
- **Rate Limits**: 10 queries per second

### Monitoring
Use the `get_api_status()` function to monitor:
- API configuration status
- Quota availability
- Error rates
- Response times

## 🛡️ Error Handling

The server provides comprehensive error handling:

```json
{
  "success": false,
  "error": "Google API Error: quotaExceeded",
  "results": [],
  "error_type": "quota_exceeded"
}
```

Common error types:
- `quota_exceeded`: Daily quota limit reached
- `invalid_api_key`: API key is invalid or missing
- `invalid_cse_id`: Custom Search Engine ID is invalid
- `network_error`: Network connectivity issues
- `api_error`: General Google API errors

## 🔄 Migration from Basic Server

To migrate from the basic server:

1. **Update imports**:
```python
# Old
from google_search_mcp_server import search_google

# New  
from enhanced_google_search_server import search_google, search_images, search_file_type
```

2. **Update configurations**: Add `GOOGLE_CSE_ID` to environment variables

3. **Leverage new features**: Start using advanced search functions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check the built-in documentation via `get_api_docs()`
- **Status Check**: Use `get_api_status()` to diagnose issues
- **Google Setup**: Follow [Google Custom Search setup guide](https://developers.google.com/custom-search/v1/introduction)

## 🔗 Related Links

- [Google Custom Search API Documentation](https://developers.google.com/custom-search/v1/reference)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [LibreChat MCP Integration Guide](https://docs.librechat.ai/)