# Specialized Extractors System Documentation

## Overview

The SimFlo MCP RAG Specialized Extractors System is a comprehensive multi-source component discovery platform that enables intelligent search and extraction of technical components, hooks, and blocks from various registries and sources.

## System Architecture

### Core Components

1. **ExtractorFactory** - Centralized factory for creating and managing extractors
2. **Specialized Extractors** - Purpose-built extractors for different source types
3. **Registry Configuration Manager** - Manages multi-source registry configurations
4. **Multi-Source Merger** - Handles conflict resolution and merging of components
5. **Category-Aware Search Service** - Intelligent search with category filtering and ranking

### Supported Source Types

- **GitHub** - Direct repository access with support for public/private repos
- **GitLab** - GitLab repositories with self-hosted instance support
- **Bitbucket** - Bitbucket repositories with workspace/repo_slug support
- **npm** - Package registry with dependency analysis
- **API** - REST API endpoints with JSON response parsing
- **Local** - Local file system and directory-based sources

## Registry Configuration

### Registry Structure

Each registry supports multiple sources of different types:

```json
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
          "branch": "main",
          "registry_file": "src/components/ui/index.ts",
          "extractor": "community"
        }
      ]
    },
    "hooks": {
      "sources": [
        {
          "name": "github_hooks",
          "type": "github",
          "url": "https://github.com/shadcn/ui",
          "branch": "main",
          "registry_file": "src/hooks/hooks.ts",
          "extractor": "shadcn_hooks"
        },
        {
          "name": "npm_registry",
          "type": "npm",
          "package_name": "@shadcn/ui-hooks",
          "extractor": "npm_hooks"
        }
      ]
    },
    "blocks": {
      "sources": [
        {
          "name": "github_blocks",
          "type": "github",
          "url": "https://github.com/shadcn/ui",
          "branch": "main",
          "registry_file": "src/blocks/blocks.json",
          "extractor": "shadcn_blocks"
        }
      ]
    }
  }
}
```

### Configuration Schema

#### Base Configuration
- `registry_name` - Unique identifier for the registry
- `registry_type` - Type of registry (component_library, ui_framework, design_system)
- `platforms` - Supported platforms (reactjs, reactnative, vue, angular)
- `description` - Registry description
- `version` - Registry version
- `maintainer` - Registry maintainer information

#### Category Configuration
- `components` - UI components category
- `hooks` - React hooks category
- `blocks` - Composite blocks category

#### Source Configuration
- `name` - Unique source identifier
- `type` - Source type (github, gitlab, bitbucket, npm, api, local)
- `url` - Source URL or endpoint
- `extractor` - Extractor type to use
- `priority` - Source priority (1-10, higher = higher priority)
- `quality_threshold` - Minimum quality score (0.0-1.0)

## Specialized Extractors

### 1. ShadcnHooksExtractor

Specialized extractor for Shadcn/UI hooks with metadata extraction and dependency analysis.

**Features:**
- Parses TypeScript/JavaScript hook files
- Extracts hook signatures and JSDoc comments
- Analyzes dependencies and peer dependencies
- Quality assessment based on code metrics
- Installation command generation

**Configuration:**
```json
{
  "type": "github",
  "extractor": "shadcn_hooks",
  "registry_file": "src/hooks/hooks.ts",
  "include_dependencies": true,
  "quality_threshold": 0.7
}
```

### 2. ShadcnBlocksExtractor

Specialized extractor for Shadcn/UI composite blocks with component relationship mapping.

**Features:**
- Parses block definitions and component relationships
- Extracts prop interfaces and default values
- Analyzes component dependencies within blocks
- Generates installation and usage instructions
- Visual block preview generation

**Configuration:**
```json
{
  "type": "github",
  "extractor": "shadcn_blocks",
  "registry_file": "src/blocks/blocks.json",
  "include_previews": true,
  "analyze_dependencies": true
}
```

### 3. NPMHooksExtractor

Specialized extractor for NPM package hooks with version analysis and dependency resolution.

**Features:**
- Analyzes NPM package structure
- Extracts hook definitions from package files
- Version compatibility analysis
- Dependency tree resolution
- License compliance checking

**Configuration:**
```json
{
  "type": "npm",
  "extractor": "npm_hooks",
  "package_name": "@example/hooks",
  "version_range": "^1.0.0",
  "analyze_dependencies": true
}
```

### 4. CommunityExtractor

Advanced extractor for community-contributed components with quality assessment and security scanning.

**Features:**
- Security vulnerability detection
- Code quality metrics analysis
- License compatibility validation
- Popularity and maintenance scoring
- Automated quality assessment

**Configuration:**
```json
{
  "type": "github",
  "extractor": "community",
  "quality_threshold": 0.8,
  "security_scan": true,
  "license_check": true
}
```

### 5. GitLabExtractor

Specialized extractor for GitLab repositories with self-hosted instance support.

**Features:**
- GitLab API integration
- Project path and repository ID handling
- Access token authentication
- Self-hosted instance support
- Branch and ref specification

**Configuration:**
```json
{
  "type": "gitlab",
  "extractor": "community",
  "project_path": "group/project",
  "access_token": "gitlab_token",
  "api_url": "https://gitlab.com/api/v4"
}
```

### 6. BitbucketExtractor

Specialized extractor for Bitbucket repositories with workspace and repository slug support.

**Features:**
- Bitbucket API v2 integration
- Workspace and repository slug handling
- Access token authentication
- Private repository support
- Branch specification

**Configuration:**
```json
{
  "type": "bitbucket",
  "extractor": "community",
  "workspace": "workspace_name",
  "repo_slug": "repository-name",
  "access_token": "bitbucket_token"
}
```

## Multi-Source Merger

### Conflict Resolution Strategies

1. **Priority-Based Resolution** - Higher priority sources override lower priority
2. **Quality-Based Resolution** - Higher quality components preferred
3. **Metadata Merging** - Combines metadata from multiple sources
4. **Source Attribution** - Maintains source provenance information

### Merging Process

1. **Component Collection** - Gather components from all sources
2. **Duplicate Detection** - Identify components with same names/types
3. **Conflict Resolution** - Apply resolution strategies
4. **Metadata Enhancement** - Merge and enhance metadata
5. **Quality Assessment** - Final quality scoring
6. **Result Compilation** - Generate final component list

## Category-Aware Search Service

### Search Features

1. **Category Filtering** - Search within specific categories (components, hooks, blocks)
2. **Semantic Matching** - Natural language understanding and relevance scoring
3. **Quality Thresholding** - Filter by minimum quality scores
4. **Platform Context** - Platform-specific result ranking
5. **Multiple Strategies** - Exact match, semantic, cross-category, weighted blend

### Search Strategies

- **Exact Match** - Precise name and description matching
- **Semantic** - Natural language understanding and similarity
- **Cross-Category** - Search across all categories with category weighting
- **Weighted Blend** - Balanced combination of all strategies

### Query Enhancement

- **Category Suggestions** - Automatic category detection and suggestions
- **Query Expansion** - Synonym and related term expansion
- **Context Awareness** - Platform and registry context integration
- **Personalization** - User preference and usage pattern integration

## Data Models

### Component Model

```python
@dataclass
class Component:
    name: str
    display_name: str
    description: str
    component_type: ComponentType
    category: ComponentCategory
    source_url: str
    documentation_url: str
    dependencies: List[str]
    metadata: Dict[str, Any]
    quality_score: float
    last_updated: datetime
    source_types: List[str]
```

### Extraction Result

```python
@dataclass
class ExtractionResult:
    success: bool
    components: List[Component]
    errors: List[str]
    warnings: List[str]
    extraction_time: float
    source_info: Dict[str, Any]
```

### Search Query

```python
@dataclass
class SearchQuery:
    query: str
    categories: List[str]
    platforms: List[str]
    registries: List[str]
    filters: SearchFilters
    strategy: str
    limit: int
```

## API Integration

### REST API Endpoints

#### Component Search
```
GET /api/v1/components/search?q={query}&category={category}&platform={platform}
```

#### Category Search
```
GET /api/v1/components/search/category?q={query}&category={category}&strategy={strategy}
```

#### Registry Management
```
GET /api/v1/registries?platform={platform}
POST /api/v1/registries/extract
```

### MCP Server Integration

The system integrates with MCP (Model Context Protocol) servers to provide AI assistants with component discovery capabilities.

**Available MCP Tools:**
- `search_components` - Search for components by query
- `get_component_details` - Get detailed component information
- `list_registries` - List available registries
- `extract_components` - Extract components from sources

## Quality Assessment

### Quality Metrics

1. **Code Quality** - Complexity, maintainability, test coverage
2. **Documentation** - Completeness, clarity, examples
3. **Popularity** - Usage, downloads, community engagement
4. **Maintenance** - Update frequency, issue resolution
5. **Security** - Vulnerability scanning, license compliance

### Scoring Algorithm

```python
quality_score = (
    code_quality * 0.3 +
    documentation_score * 0.25 +
    popularity_score * 0.2 +
    maintenance_score * 0.15 +
    security_score * 0.1
)
```

## Security Features

### Vulnerability Scanning

- Dependency vulnerability detection
- Code security pattern analysis
- License compliance checking
- Malicious code detection

### Access Control

- API key authentication
- Rate limiting and throttling
- Source access validation
- Secure credential storage

## Usage Examples

### Basic Component Search

```python
# Search for button components
results = await category_search_service.search_components(
    SearchQuery(
        query="button component",
        categories=["components"],
        platforms=["reactjs"],
        strategy="weighted"
    ),
    limit=10
)
```

### Registry Configuration

```python
# Load registry configuration
config_manager = RegistryConfigManager()
registry_config = config_manager.load_registry_config("shadcn_ui")

# Extract components from all sources
factory = ExtractorFactory()
results = await factory.extract_from_registry(registry_config)
```

### Custom Extractor

```python
# Create custom extractor
class CustomExtractor(BaseExtractor):
    async def extract(self) -> ExtractionResult:
        # Custom extraction logic
        return ExtractionResult(
            success=True,
            components=extracted_components,
            errors=[],
            warnings=[],
            extraction_time=time.time()
        )
```

## Testing and Validation

### Test Framework

Comprehensive testing framework with:

- Unit tests for individual extractors
- Integration tests for the complete pipeline
- Performance tests for scalability validation
- Security tests for vulnerability detection

### Validation Scripts

```bash
# Run all tests
npm test

# Test specific extractor
python scripts/test_gitlab_bitbucket_extractors.py

# Validate registry configurations
python scripts/validate_registry_configs.py
```

## Performance Optimization

### Caching Strategy

- Component metadata caching
- Search result caching
- Registry configuration caching
- API response caching

### Optimization Techniques

- Parallel extraction from multiple sources
- Incremental updates and delta processing
- Efficient memory management
- Background processing queues

## Deployment and Monitoring

### Production Deployment

- Container-based deployment with Docker
- Load balancing and horizontal scaling
- Database clustering for high availability
- CDN integration for global performance

### Monitoring and Alerting

- Performance metrics collection
- Error rate monitoring
- Resource usage tracking
- Automated alerting and notifications

## Future Enhancements

### Planned Features

1. **Additional Source Types** - Support for more registries and platforms
2. **Advanced Search** - AI-powered search with better understanding
3. **Real-time Updates** - Live synchronization with source repositories
4. **Collaborative Features** - Community contributions and ratings
5. **Analytics Dashboard** - Usage statistics and insights

### Expansion Plans

- Support for additional frameworks (Vue, Angular, Svelte)
- Mobile-native component libraries
- Design system integration
- Enterprise features and security

## Contributing

### Development Setup

1. Clone the repository
2. Install dependencies: `npm install`
3. Run development server: `npm run dev`
4. Run tests: `npm test`

### Code Standards

- TypeScript for type safety
- ESLint for code quality
- Prettier for code formatting
- Comprehensive test coverage

## License and Support

- MIT License
- Community support through GitHub issues
- Enterprise support available
- Regular updates and maintenance

---

This documentation provides a comprehensive overview of the Specialized Extractors System. For specific implementation details and API references, please refer to the source code and inline documentation.