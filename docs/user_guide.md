# User Guide - SimFlo MCP RAG Specialized Extractors

## Getting Started

Welcome to the SimFlo MCP RAG Specialized Extractors system! This guide will help you understand how to use the powerful component discovery and search capabilities.

## Quick Start

### 1. System Overview

The system enables you to:
- Search for components, hooks, and blocks across multiple registries
- Extract components from various sources (GitHub, GitLab, Bitbucket, npm, APIs)
- Get intelligent recommendations based on your context
- Access quality-assessed and security-scanned components

### 2. Basic Usage

#### Via MCP Server (AI Assistants)

```bash
# Available MCP tools:
- search_components: Search for components by query
- get_component_details: Get detailed component information
- list_registries: List available registries
- extract_components: Extract components from sources
```

#### Via REST API

```bash
# Search for components
curl "http://localhost:8000/api/v1/components/search?q=button&platform=reactjs"

# Get component details
curl "http://localhost:8000/api/v1/components/button?registry=shadcn_db"

# List registries
curl "http://localhost:8000/api/v1/registries?platform=reactjs"
```

## Search Capabilities

### 1. Basic Search

```python
# Search for components
results = await search_components(
    query="button component",
    platform="reactjs",
    limit=10
)
```

### 2. Category-Aware Search

```python
# Search in specific categories
results = await search_components_by_category(
    query="mobile navigation",
    category="components",
    platform="reactjs",
    strategy="weighted"
)
```

### 3. Advanced Filtering

```python
# Search with quality threshold
results = await search_components(
    query="form input",
    platform="reactjs",
    quality_threshold=0.8,
    limit=5
)
```

## Search Strategies

The system supports multiple search strategies:

### 1. Exact Match
- Best for precise component names
- Fast and accurate for known components
- Example: "button", "input", "modal"

### 2. Semantic Search
- Natural language understanding
- Finds related components
- Example: "something for user input" → finds input components

### 3. Cross-Category
- Search across all component types
- Useful when unsure of component category
- Example: "navigation" → finds components, hooks, and blocks

### 4. Weighted Blend
- Balanced approach combining all strategies
- Default and recommended for most searches
- Provides best overall results

## Registry Management

### 1. Available Registries

The system includes several pre-configured registries:

- **shadcn_db** - Shadcn/UI components
- **gluestack_db** - Gluestack UI components
- **radix_db** - Radix UI components

### 2. Registry Information

```python
# Get registry information
registries = await list_registries(platform="reactjs")

# Each registry contains:
- Registry name and type
- Supported platforms
- Available categories (components, hooks, blocks)
- Source information
- Quality metrics
```

## Component Categories

### 1. Components
- UI elements (Button, Input, Modal, etc.)
- Layout components (Header, Sidebar, etc.)
- Form components (Form, Select, etc.)
- Data display components (Table, Card, etc.)

### 2. Hooks
- React hooks for functionality
- State management hooks
- Lifecycle hooks
- Custom utility hooks

### 3. Blocks
- Composite components
- Pre-built layouts
- Feature-complete sections
- Dashboard components

## Quality Assessment

### 1. Quality Scores

Each component receives a quality score (0.0-1.0) based on:

- **Code Quality** (30%): Complexity, maintainability, test coverage
- **Documentation** (25%): Completeness, clarity, examples
- **Popularity** (20%): Usage, downloads, community engagement
- **Maintenance** (15%): Update frequency, issue resolution
- **Security** (10%): Vulnerability scanning, license compliance

### 2. Quality Tiers

- **Excellent** (0.9-1.0): Production-ready, well-maintained
- **Good** (0.7-0.9): Suitable for most use cases
- **Fair** (0.5-0.7): Usable with some limitations
- **Poor** (0.0-0.5): Use with caution

## Platform Support

### 1. React JS
- Full component support
- Hook compatibility
- Modern React features

### 2. React Native
- Mobile-optimized components
- Native platform integration
- Cross-platform compatibility

## Context-Aware Features

### 1. Platform Context

The system adapts results based on your platform:

```python
# React JS context
search_components("button", platform="reactjs")
# Returns: web-optimized button components

# React Native context
search_components("button", platform="reactnative")
# Returns: mobile-optimized button components
```

### 2. Category Suggestions

The system can suggest the best category for your query:

```python
# Get category suggestions
suggestions = await get_category_suggestions("user authentication")
# Returns: ["hooks", "components", "blocks"]
```

## Component Details

### 1. Getting Component Information

```python
# Get detailed component information
component = await get_component_details("button", registry="shadcn_db")

# Includes:
- Name and display name
- Description and usage
- Installation instructions
- Dependencies and requirements
- Code examples
- Quality metrics
- Source information
```

### 2. Installation Information

```python
# Get installation instructions
install_info = await get_component_installation("button", registry="shadcn_db")

# Includes:
- Package names and versions
- Installation commands
- Configuration steps
- Dependencies
- Import statements
```

## Best Practices

### 1. Effective Searching

- Use specific terms for exact matches
- Use natural language for semantic search
- Specify platform when possible
- Use quality thresholds for production use

### 2. Component Selection

- Check quality scores before use
- Review documentation and examples
- Verify compatibility with your platform
- Consider maintenance status

### 3. Integration

- Follow installation instructions carefully
- Test components in your environment
- Check for dependency conflicts
- Monitor for updates

## Common Use Cases

### 1. Finding UI Components

```python
# Find button components
results = await search_components("button", category="components", platform="reactjs")

# Find form components
results = await search_components("form input", category="components", platform="reactjs")
```

### 2. Finding Hooks

```python
# Find state management hooks
results = await search_components("state management", category="hooks", platform="reactjs")

# Find lifecycle hooks
results = await search_components("component lifecycle", category="hooks", platform="reactjs")
```

### 3. Finding Blocks

```python
# Find layout blocks
results = await search_components("dashboard layout", category="blocks", platform="reactjs")

# Find feature blocks
results = await search_components("user profile", category="blocks", platform="reactjs")
```

## Troubleshooting

### 1. Common Issues

**No Results Found**
- Try broader search terms
- Check spelling and syntax
- Try different search strategies
- Verify platform compatibility

**Poor Quality Results**
- Increase quality threshold
- Try semantic search
- Check category filters
- Verify registry configuration

**Slow Performance**
- Reduce result limit
- Use specific search terms
- Check network connectivity
- Verify server status

### 2. Getting Help

- Check system logs for errors
- Verify API connectivity
- Test with simple queries
- Contact support for persistent issues

## Advanced Features

### 1. Custom Registries

You can configure custom registries:

```python
# Add custom registry
custom_registry = {
    "registry_name": "my_components",
    "registry_type": "component_library",
    "platforms": ["reactjs"],
    "categories": {
        "components": {
            "sources": [
                {
                    "name": "my_github",
                    "type": "github",
                    "url": "https://github.com/myorg/components",
                    "extractor": "community"
                }
            ]
        }
    }
}
```

### 2. Batch Operations

```python
# Search multiple queries at once
queries = ["button", "input", "modal"]
results = await batch_search(queries, platform="reactjs")
```

### 3. Personalization

The system learns from your usage patterns:

- Frequently searched components
- Preferred quality levels
- Platform preferences
- Category biases

## API Reference

### Search Endpoints

#### GET /api/v1/components/search
```python
# Search components
response = requests.get(
    "http://localhost:8000/api/v1/components/search",
    params={
        "q": "button",
        "platform": "reactjs",
        "limit": 10,
        "quality_threshold": 0.7
    }
)
```

#### GET /api/v1/components/search/category
```python
# Category-aware search
response = requests.get(
    "http://localhost:8000/api/v1/components/search/category",
    params={
        "q": "navigation",
        "category": "components",
        "platform": "reactjs",
        "strategy": "weighted"
    }
)
```

### Component Endpoints

#### GET /api/v1/components/{component_name}
```python
# Get component details
response = requests.get(
    "http://localhost:8000/api/v1/components/button",
    params={"registry": "shadcn_db"}
)
```

#### GET /api/v1/components/{component_name}/installation
```python
# Get installation info
response = requests.get(
    "http://localhost:8000/api/v1/components/button/installation",
    params={"registry": "shadcn_db"}
)
```

### Registry Endpoints

#### GET /api/v1/registries
```python
# List registries
response = requests.get(
    "http://localhost:8000/api/v1/registries",
    params={"platform": "reactjs"}
)
```

## Examples

### Example 1: Building a Form

```python
# Search for form components
form_components = await search_components(
    query="form input validation",
    category="components",
    platform="reactjs",
    limit=5
)

# Get details for each component
for component in form_components:
    details = await get_component_details(component.name, "shadcn_db")
    print(f"Component: {details.display_name}")
    print(f"Description: {details.description}")
    print(f"Quality Score: {details.quality_score}")
    print("---")
```

### Example 2: Finding Navigation Components

```python
# Search for navigation components
nav_components = await search_components_by_category(
    query="mobile navigation menu",
    category="components",
    platform="reactnative",
    strategy="semantic",
    limit=3
)

# Get installation instructions
for component in nav_components:
    install_info = await get_component_installation(
        component.name,
        "gluestack_db"
    )
    print(f"Install: {install_info.install_commands}")
```

### Example 3: Quality-Filtered Search

```python
# Find high-quality hooks
quality_hooks = await search_components(
    query="state management",
    category="hooks",
    platform="reactjs",
    quality_threshold=0.8,
    limit=10
)

print(f"Found {len(quality_hooks)} high-quality hooks")
```

## Performance Tips

### 1. Optimizing Searches

- Use specific terms for faster results
- Set appropriate limits to reduce overhead
- Use quality thresholds to filter early
- Cache results for repeated searches

### 2. Batch Operations

- Group related searches together
- Use batch endpoints for multiple queries
- Process results asynchronously
- Implement client-side caching

### 3. Resource Management

- Monitor API usage and rate limits
- Implement proper error handling
- Use connection pooling for HTTP clients
- Clean up resources properly

## Security Considerations

### 1. API Security

- Use authentication tokens when available
- Validate all input parameters
- Implement proper error handling
- Monitor for suspicious activity

### 2. Component Security

- Check quality scores before use
- Review component source code
- Verify license compatibility
- Monitor for security updates

### 3. Data Privacy

- Avoid logging sensitive information
- Use secure connections (HTTPS)
- Implement proper access controls
- Follow data protection regulations

## Conclusion

The SimFlo MCP RAG Specialized Extractors system provides powerful component discovery capabilities with intelligent search, quality assessment, and multi-source extraction. By following this guide, you can effectively leverage the system to find and integrate high-quality components into your projects.

For additional support and documentation, please refer to the system documentation or contact the development team.

---

Happy component hunting! 🚀