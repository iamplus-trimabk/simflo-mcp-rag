# Developer Quick Reference - SimFlo MCP RAG Specialized Extractors

## Core Components Quick Reference

### ExtractorFactory

```python
from extractors.extractor_factory import get_extractor_factory

# Get factory instance
factory = get_extractor_factory()

# Create extractor
extractor = factory.create_extractor("community", source_config)

# Test extractor
result = factory.test_extractor("community", source_config)

# Get available extractors
extractors = factory.get_available_extractors()

# Recommend extractor for source
recommendations = factory.recommend_extractors(source_config)
```

### Registry Configuration

```python
from services.registry_config_manager import RegistryConfigManager

# Load registry configuration
config_manager = RegistryConfigManager()
registry_config = config_manager.load_registry_config("shadcn_ui")

# Get registry sources
sources = registry_config.categories.components.sources

# Extract from registry
results = await factory.extract_from_registry(registry_config)
```

### Category-Aware Search

```python
from services.category_search_service import CategorySearchService

# Initialize search service
search_service = CategorySearchService()

# Create search query
query = SearchQuery(
    query="button component",
    categories=["components"],
    platforms=["reactjs"],
    filters=SearchFilters(quality_threshold=0.7),
    strategy="weighted",
    limit=10
)

# Perform search
results = await search_service.search_components(query)
```

## Available Extractors

### ShadcnHooksExtractor
```python
# For Shadcn/UI hooks extraction
extractor = factory.create_extractor("shadcn_hooks", {
    "type": "github",
    "url": "https://github.com/shadcn/ui",
    "registry_file": "src/hooks/hooks.ts"
})
```

### ShadcnBlocksExtractor
```python
# For Shadcn/UI blocks extraction
extractor = factory.create_extractor("shadcn_blocks", {
    "type": "github",
    "url": "https://github.com/shadcn/ui",
    "registry_file": "src/blocks/blocks.json"
})
```

### NPMHooksExtractor
```python
# For NPM package hooks extraction
extractor = factory.create_extractor("npm_hooks", {
    "type": "npm",
    "package_name": "@example/hooks"
})
```

### CommunityExtractor
```python
# For community components extraction
extractor = factory.create_extractor("community", {
    "type": "github",
    "url": "https://github.com/user/repo",
    "quality_threshold": 0.8
})
```

### GitLabExtractor
```python
# For GitLab repositories
extractor = factory.create_extractor("community", {
    "type": "gitlab",
    "project_path": "group/project",
    "access_token": "gitlab_token"
})
```

### BitbucketExtractor
```python
# For Bitbucket repositories
extractor = factory.create_extractor("community", {
    "type": "bitbucket",
    "workspace": "workspace_name",
    "repo_slug": "repository-name"
})
```

## Data Models

### Component
```python
from models import Component, ComponentType, ComponentCategory

component = Component(
    name="button",
    display_name="Button",
    description="A button component",
    component_type=ComponentType.COMPONENT,
    category=ComponentCategory.COMPONENTS,
    source_url="https://github.com/example/button",
    documentation_url="https://docs.example.com/button",
    dependencies=["@example/ui"],
    metadata={},
    quality_score=0.9,
    last_updated=datetime.now(),
    source_types=["github"]
)
```

### SearchQuery
```python
from services.category_search_service import SearchQuery, SearchFilters

query = SearchQuery(
    query="search term",
    categories=["components", "hooks"],
    platforms=["reactjs", "reactnative"],
    registries=["shadcn_db", "gluestack_db"],
    filters=SearchFilters(
        quality_threshold=0.7,
        platforms=["reactjs"],
        source_types=["github"]
    ),
    strategy="weighted",
    limit=10
)
```

### ExtractionResult
```python
from extractors.base_extractor import ExtractionResult

result = ExtractionResult(
    success=True,
    components=[component1, component2],
    errors=[],
    warnings=[],
    extraction_time=1.5,
    source_info=source_config
)
```

## API Server Integration

### Adding New Endpoints
```python
# In api_server.py
@app.get("/api/v1/custom-endpoint")
async def custom_endpoint():
    # Your logic here
    return {"success": True, "data": result}
```

### Using Category Search Service
```python
@app.get("/api/v1/components/search/category")
async def search_components_by_category(
    q: str = Query(...),
    category: str = Query(...),
    platform: Optional[str] = Query(None),
    limit: int = Query(10),
    quality_threshold: float = Query(0.0),
    strategy: str = Query("weighted")
):
    search_service = CategorySearchService()
    query = SearchQuery(
        query=q,
        categories=[category],
        platforms=[platform] if platform else [],
        filters=SearchFilters(quality_threshold=quality_threshold),
        strategy=strategy,
        limit=limit
    )
    results = await search_service.search_components(query)
    return APIResponse(data=results)
```

## MCP Server Integration

### Adding New Tools
```python
# In mcp-server/src/index.ts
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "new_tool",
        description: "Tool description",
        inputSchema: {
          type: "object",
          properties: {
            param1: { type: "string", description: "Parameter 1" }
          },
          required: ["param1"]
        }
      }
    ]
  }
})
```

### Handling Tool Calls
```python
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params

  if (name === "new_tool") {
    // Handle tool call
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(result)
        }
      ]
    }
  }
})
```

## Testing

### Unit Tests
```python
# Test extractor
import pytest
from extractors.community_extractor import CommunityExtractor

@pytest.mark.asyncio
async def test_community_extractor():
    config = {"type": "github", "url": "https://github.com/test/repo"}
    extractor = CommunityExtractor(config)

    async with extractor:
        result = await extractor.extract()
        assert result.success is True
        assert len(result.components) > 0
```

### Integration Tests
```python
# Test search service
@pytest.mark.asyncio
async def test_category_search():
    search_service = CategorySearchService()
    query = SearchQuery(
        query="button",
        categories=["components"],
        platforms=["reactjs"],
        limit=5
    )

    results = await search_service.search_components(query)
    assert len(results) > 0
    assert all(r.quality_score >= 0.0 for r in results)
```

### API Tests
```python
# Test API endpoints
import httpx
import pytest

@pytest.mark.asyncio
async def test_search_endpoint():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8000/api/v1/components/search",
            params={"q": "button", "limit": 5}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
```

## Configuration

### Registry Configuration Format
```json
{
  "registry_name": "example_registry",
  "registry_type": "component_library",
  "platforms": ["reactjs", "reactnative"],
  "categories": {
    "components": {
      "sources": [
        {
          "name": "github_source",
          "type": "github",
          "url": "https://github.com/example/components",
          "branch": "main",
          "registry_file": "src/components/index.ts",
          "extractor": "community",
          "priority": 1,
          "quality_threshold": 0.7
        }
      ]
    },
    "hooks": {
      "sources": [
        {
          "name": "npm_source",
          "type": "npm",
          "package_name": "@example/hooks",
          "extractor": "npm_hooks",
          "priority": 2
        }
      ]
    }
  }
}
```

### Environment Variables
```bash
# API Server
SERVICE_MODE=single
LOGIC_SERVICE_PORT=3001
LOGIC_SERVICE_HOST=localhost
LOGIC_SERVICE_PROTOCOL=ws
UI_THEME=auto
ENABLE_METRICS=true
LOG_LEVEL=info

# Database (if used)
DATABASE_URL=sqlite:///./simflo_rag.db
```

## Error Handling

### Common Error Patterns
```python
try:
    extractor = factory.create_extractor("community", config)
    async with extractor:
        result = await extractor.extract()
        if not result.success:
            logger.error(f"Extraction failed: {result.errors}")
            return None
        return result.components
except Exception as e:
    logger.error(f"Extractor creation failed: {e}")
    return None
```

### Validation
```python
# Validate source configuration
if not extractor.validate_source():
    logger.error("Invalid source configuration")
    return None

# Validate registry configuration
if not config_manager.validate_registry_config(registry_config):
    logger.error("Invalid registry configuration")
    return None
```

## Performance Optimization

### Caching
```python
# Component caching
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_cached_components(registry: str, category: str):
    return load_components(registry, category)

# Search result caching
@lru_cache(maxsize=500)
def cached_search(query: str, category: str, limit: int):
    return perform_search(query, category, limit)
```

### Async Operations
```python
# Parallel extraction
async def extract_from_multiple_sources(sources):
    tasks = []
    for source in sources:
        extractor = factory.create_extractor(source["extractor"], source)
        tasks.append(extractor.extract())

    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [r for r in results if not isinstance(r, Exception)]
```

## Debugging

### Logging
```python
import logging
from utils.logger import setup_logging

# Setup logging
setup_logging(level="DEBUG")

# Debug extractor
logger = logging.getLogger(__name__)
logger.debug(f"Creating extractor for config: {config}")
logger.debug(f"Extractor created: {extractor}")
```

### Debug Mode
```python
# Enable debug mode
import os
os.environ["DEBUG"] = "1"

# Verbose logging
logger.debug(f"Search query: {query}")
logger.debug(f"Search results: {results}")
```

## Common Patterns

### Extractor Pattern
```python
class CustomExtractor(BaseExtractor):
    def __init__(self, source_config):
        super().__init__(source_config)
        # Initialize extractor-specific properties

    async def extract(self) -> ExtractionResult:
        try:
            # Extraction logic
            components = await self._extract_components()
            return ExtractionResult(
                success=True,
                components=components,
                errors=[],
                warnings=[],
                extraction_time=time.time()
            )
        except Exception as e:
            return ExtractionResult(
                success=False,
                components=[],
                errors=[str(e)],
                warnings=[],
                extraction_time=0.0,
                source_info=self.source_config
            )
```

### Service Pattern
```python
class CustomService:
    def __init__(self):
        self.factory = get_extractor_factory()
        self.config_manager = RegistryConfigManager()

    async def process_request(self, request):
        # Process request logic
        registry_config = self.config_manager.load_registry_config(request.registry)
        results = await self.factory.extract_from_registry(registry_config)
        return self._format_results(results)
```

## Utility Functions

### Component Utilities
```python
from utils.component_utils import (
    format_display_name,
    determine_component_type,
    determine_component_category,
    calculate_quality_score
)

# Format component name
display_name = format_display_name("button-primary")  # "Button Primary"

# Determine component type
component_type = determine_component_type("ui")  # ComponentType.COMPONENT

# Calculate quality score
quality_score = calculate_quality_score(component)  # 0.85
```

### Search Utilities
```python
from utils.search_utils import (
    normalize_query,
    expand_query,
    calculate_relevance_score,
    filter_by_quality
)

# Normalize search query
normalized = normalize_query("  Button  Component  ")  # "button component"

# Expand query with synonyms
expanded = expand_query("button")  # ["button", "btn", "button component"]

# Calculate relevance score
score = calculate_relevance_score(query, component)  # 0.92

# Filter by quality
filtered = filter_by_quality(components, 0.7)  # Components with score >= 0.7
```

## Migration Guide

### From v1 to v2
```python
# Old way (v1)
components = await search_components(query, limit=10)

# New way (v2)
search_service = CategorySearchService()
query = SearchQuery(
    query=query,
    categories=["components"],
    limit=10
)
results = await search_service.search_components(query)
```

### Configuration Migration
```python
# Old format
{
  "name": "shadcn_ui",
  "url": "https://github.com/shadcn/ui",
  "type": "github"
}

# New format
{
  "registry_name": "shadcn_ui",
  "registry_type": "component_library",
  "platforms": ["reactjs", "reactnative"],
  "categories": {
    "components": {
      "sources": [
        {
          "name": "github_main",
          "type": "github",
          "url": "https://github.com/shadcn/ui",
          "extractor": "community"
        }
      ]
    }
  }
}
```

## Best Practices

### Code Organization
```
project/
├── extractors/          # Extractor implementations
├── services/           # Business logic services
├── models/             # Data models
├── utils/              # Utility functions
├── tests/              # Test files
└── docs/               # Documentation
```

### Naming Conventions
```python
# Extractors: [Source]Extractor
class GitHubExtractor(BaseExtractor)
class GitLabExtractor(BaseExtractor)

# Services: [Feature]Service
class CategorySearchService
class RegistryConfigManager

# Models: PascalCase
class Component
class ExtractionResult

# Functions: snake_case
def extract_components()
def search_components()
```

### Error Handling
```python
# Always handle exceptions
try:
    result = await risky_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}")
    return None

# Validate inputs
if not config or not config.get("url"):
    raise ValueError("Invalid configuration")

# Log important events
logger.info(f"Processed {len(components)} components")
```

This quick reference provides the essential information you need to work with the SimFlo MCP RAG Specialized Extractors system. For detailed documentation, please refer to the main documentation files.