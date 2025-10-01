# Content Collection System - Complete Guide

## Purpose
Content discovery and acquisition system for gathering information from various sources. Provides the source discovery and content fetching capabilities that feed into the RAG pipeline.

## Position in v2 Architecture
This is component **03** in the v2 numbered system:
- **00-rag-registry**: Registry-based RAG database management
- **01-mcp-server**: AI assistant integration via CLI
- **02-rag-builder**: Pipeline orchestration and RAG construction
- **03-content-collection**: Source discovery and content acquisition (✅ Complete)
- **04-extractors**: Content extraction from various sources

## Components

### source-discovery/
Automated source discovery and validation capabilities:
- **GitHub Repository Discovery**: Find relevant repositories
- **NPM Package Discovery**: Discover useful packages and libraries
- **Documentation Site Discovery**: Identify documentation resources
- **Community Resource Discovery**: Find tutorials, guides, and examples

### content-fetching/
Content acquisition and download tools:
- **Repository Cloning**: Git-based content retrieval
- **Web Scraping**: Documentation and guide extraction
- **API Integration**: Package information retrieval
- **File Downloads**: Asset and resource acquisition

## CLI Interface

### Core Commands

#### discover - Discover sources for content
```bash
# Discover GitHub repositories for React components
python3 v2/03-content-collection/content_collection_cli.py discover --query "react components" --source-type github --limit 10 --format json

# Discover NPM packages for React hooks
python3 v2/03-content-collection/content_collection_cli.py discover --query "react hooks" --source-type npm --limit 15 --format json

# Discover documentation sites
python3 v2/03-content-collection/content_collection_cli.py discover --query "react documentation" --source-type docs --limit 5 --format json
```

**Parameters**:
- `--query`: Search query for discovering sources (required)
- `--source-type`: Type of sources to discover (github, npm, docs, community)
- `--limit`: Maximum number of sources to return (default: 10)
- `--format`: Output format (json, table)

**Response Example**:
```json
{
  "success": true,
  "timestamp": "2025-09-30T21:37:01.043963",
  "data": {
    "query": "react components",
    "source_type": "github",
    "total_found": 10,
    "sources": [
      {
        "name": "shadcn-ui/ui",
        "type": "github",
        "url": "https://github.com/shadcn-ui/ui",
        "description": "Beautifully designed components built with Radix UI and Tailwind CSS",
        "stars": 25000,
        "language": "TypeScript",
        "updated_at": "2025-09-25T10:30:00Z",
        "relevance_score": 0.95
      }
    ]
  }
}
```

#### fetch - Fetch content from discovered sources
```bash
# Fetch content from sources file
python3 v2/03-content-collection/content_collection_cli.py fetch --sources-file sources.json --output-dir raw_content/ --format json

# Fetch content from specific source
python3 v2/03-content-collection/content_collection_cli.py fetch --source "https://github.com/shadcn-ui/ui" --output-dir raw_content/shadcn/

# Fetch content with depth control
python3 v2/03-content-collection/content_collection_cli.py fetch --sources-file sources.json --output-dir raw_content/ --depth 1 --format json
```

**Parameters**:
- `--sources-file`: JSON file containing discovered sources
- `--source`: Single source URL to fetch (alternative to sources-file)
- `--output-dir`: Directory to store fetched content (required)
- `--depth`: Fetch depth for repositories (default: 1)
- `--format`: Output format (json, table)

#### status - Get system status
```bash
# Get overall system status
python3 v2/03-content-collection/content_collection_cli.py status --format json

# Get status with detailed information
python3 v2/03-content-collection/content_collection_cli.py status --detailed --format json
```

**Response Example**:
```json
{
  "success": true,
  "timestamp": "2025-09-30T21:37:01.043963",
  "data": {
    "system_status": "operational",
    "supported_source_types": ["github", "npm", "docs", "community"],
    "last_discovery": "2025-09-30T20:00:00Z",
    "total_sources_discovered": 156,
    "total_content_fetched": "2.3GB",
    "available_storage": "15.2GB",
    "active_fetches": 0,
    "queue_status": "empty"
  }
}
```

#### list-source-types - List available source types
```bash
# List all supported source types
python3 v2/03-content-collection/content_collection_cli.py list-source-types --format json

# Get detailed information about source types
python3 v2/03-content-collection/content_collection_cli.py list-source-types --detailed --format json
```

**Response Example**:
```json
{
  "success": true,
  "timestamp": "2025-09-30T21:37:01.043963",
  "data": {
    "supported_types": [
      {
        "type": "github",
        "name": "GitHub Repositories",
        "description": "Source code repositories from GitHub",
        "supported_features": ["cloning", "file_list", "metadata", "releases"],
        "authentication": "token_optional",
        "rate_limits": "GitHub API limits apply"
      },
      {
        "type": "npm",
        "name": "NPM Packages",
        "description": "Node.js packages and libraries",
        "supported_features": ["package_info", "dependencies", "documentation", "downloads"],
        "authentication": "none_required",
        "rate_limits": "NPM registry limits apply"
      },
      {
        "type": "docs",
        "name": "Documentation Sites",
        "description": "Online documentation and guides",
        "supported_features": ["scraping", "content_extraction", "search"],
        "authentication": "none_required",
        "rate_limits": "Site-specific limits apply"
      }
    ]
  }
}
```

### Command Pipeline Integration

#### Pipeline Example
```bash
# Discover sources and fetch content in pipeline
python3 v2/03-content-collection/content_collection_cli.py discover --query "react components" --source-type github --limit 5 | \
python3 v2/03-content-collection/content_collection_cli.py fetch --sources - --output-dir raw_content/
```

#### Multi-Stage Discovery
```bash
# Stage 1: Discover repositories
python3 v2/03-content-collection/content_collection_cli.py discover --query "shadcn components" --source-type github --limit 3 --output sources_stage1.json

# Stage 2: Discover related packages
python3 v2/03-content-collection/content_collection_cli.py discover --query "react form validation" --source-type npm --limit 5 --output sources_stage2.json

# Stage 3: Fetch all content
python3 v2/03-content-collection/content_collection_cli.py fetch --sources-file sources_stage1.json --output-dir stage1_content/
python3 v2/03-content-collection/content_collection_cli.py fetch --sources-file sources_stage2.json --output-dir stage2_content/
```

## Content Types

### Source Discovery Types

#### GitHub Repositories
- **Component Libraries**: React, Vue, Angular component libraries
- **UI Frameworks**: Bootstrap, Material-UI, Tailwind CSS implementations
- **Template Repositories**: Project templates and boilerplates
- **Example Projects**: Demonstrative applications and examples
- **Tool Libraries**: Development tools and utilities

**Discovery Methods**:
- GitHub API search with advanced filters
- Topic-based repository discovery
- Trending repository analysis
- Social graph analysis (related repositories)

#### NPM Packages
- **Component Libraries**: Pre-built component packages
- **Utility Libraries**: Helper functions and tools
- **Hook Libraries**: Custom React hooks
- **Development Tools**: Build and development utilities
- **Template Packages**: Project templates and generators

**Discovery Methods**:
- NPM registry search and filtering
- Package dependency analysis
- Download statistics and trends
- Related package recommendations

#### Documentation Sites
- **Official Documentation**: Framework and library documentation
- **Tutorial Sites**: Learning resources and guides
- **Blog Posts**: Technical articles and tutorials
- **API References**: Complete API documentation
- **Community Guides**: Community-contributed content

**Discovery Methods**:
- Web search integration
- API documentation discovery
- RSS feed monitoring
- Community site indexing

#### Community Resources
- **CodeSandbox Examples**: Interactive code examples
- **Stack Overflow**: Q&A content and solutions
- **Dev.to Articles**: Community tutorials and articles
- **Medium Posts**: Technical blog posts
- **YouTube Tutorials**: Video content and screencasts

**Discovery Methods**:
- Community platform APIs
- Content aggregation services
- Social media monitoring
- RSS feed subscriptions

### Content Fetching Types

#### Repository Cloning
- **Git Cloning**: Full repository cloning with history
- **Shallow Cloning**: Latest version only for efficiency
- **Sparse Checkout**: Clone specific directories or files
- **Submodule Handling**: Recursive submodule management
- **Branch/Tag Checkout**: Specific version checkout

#### Web Scraping
- **HTML Parsing**: Extract content from web pages
- **JavaScript Rendering**: Handle dynamic content
- **Multi-page Crawling**: Follow links within sites
- **Rate Limiting**: Respectful scraping with delays
- **Content Cleaning**: Remove navigation and ads

#### API Integration
- **REST API Calls**: Structured data retrieval
- **GraphQL Queries**: Efficient data fetching
- **Authentication Handling**: OAuth, API keys, tokens
- **Rate Limit Management**: Automatic retry and backoff
- **Data Validation**: Schema validation for API responses

#### File Downloads
- **Direct Downloads**: File download from URLs
- **Batch Downloads**: Multiple file processing
- **Resume Support**: Resume interrupted downloads
- **Compression Handling**: Archive extraction and processing
- **Virus Scanning**: Security scanning of downloaded content

## Integration with Other Components

### Upstream Integration
The content collection system integrates with:
- **External APIs**: GitHub API, NPM registry, documentation sites
- **Web Sources**: Documentation sites, blogs, tutorials
- **Community Platforms**: Stack Overflow, Dev.to, Medium
- **File Storage**: Local file system, cloud storage

### Downstream Integration
The content collection system provides source material for:
- **04-extractors**: Uses discovered sources for content extraction
- **02-rag-builder**: Processes extracted content into RAG databases
- **00-rag-registry**: Stores processed content in registry-based structure

### Data Flow
```
External Sources → Content Collection → Content Fetching → Extractors → RAG Builder → Registry Storage
```

## Configuration and Management

### Environment Variables
- `CONTENT_ROOT`: Root directory for content storage
- `GITHUB_TOKEN`: GitHub API token for increased limits
- `NPM_TOKEN`: NPM authentication token (if needed)
- `USER_AGENT`: Custom user agent for web requests
- `RATE_LIMIT_DELAY`: Delay between requests in seconds

### Configuration Files
- `config/sources.json`: Source type configurations
- `config/filters.json`: Content filtering rules
- `config/storage.json`: Storage and retention policies
- `config/auth.json`: Authentication credentials

## Performance and Scalability

### Optimization Features
- **Concurrent Fetching**: Parallel content downloads
- **Caching**: Local caching of fetched content
- **Incremental Updates**: Only fetch new or changed content
- **Compression**: Compress stored content to save space
- **Deduplication**: Remove duplicate content across sources

### Monitoring and Metrics
- **Fetch Success Rate**: Track successful vs failed fetches
- **Content Volume**: Monitor storage usage and growth
- **Processing Time**: Track time for discovery and fetching
- **Error Rates**: Monitor error types and frequencies
- **Source Health**: Track source availability and reliability

## Quality Assurance

### Content Validation
- **Format Validation**: Ensure content is in expected formats
- **Size Limits**: Prevent excessively large downloads
- **Type Checking**: Verify content types match expectations
- **Security Scanning**: Basic security checks on downloaded content
- **Integrity Verification**: Check for corrupted or incomplete content

### Source Filtering
- **Quality Filters**: Exclude low-quality or spam sources
- **Relevance Scoring**: Rank sources by relevance to query
- **Freshness Filters**: Prioritize recently updated content
- **Popularity Filters**: Include popular and well-maintained sources
- **Language Filters**: Filter by programming language or content language

## Error Handling and Recovery

### Common Error Scenarios
- **Network Issues**: Handle connectivity problems and timeouts
- **API Rate Limits**: Respect and handle rate limiting
- **Authentication Failures**: Handle expired or invalid credentials
- **Storage Issues**: Handle disk space limitations
- **Source Unavailability**: Handle removed or moved sources

### Recovery Strategies
- **Automatic Retry**: Retry failed requests with exponential backoff
- **Fallback Sources**: Use alternative sources when primary fails
- **Partial Recovery**: Recover successfully fetched content
- **Error Logging**: Comprehensive error logging for debugging
- **Graceful Degradation**: Continue operation with reduced functionality

## Best Practices

### Discovery Best Practices
- **Specific Queries**: Use detailed and specific search queries
- **Multiple Sources**: Discover from multiple source types
- **Quality Filtering**: Apply strict quality and relevance filters
- **Regular Updates**: Periodically refresh discovered sources
- **Source Diversity**: Include diverse types of sources

### Fetching Best Practices
- **Incremental Updates**: Only fetch new or changed content
- **Respectful Access**: Follow robots.txt and rate limits
- **Storage Management**: Regular cleanup of old or unused content
- **Backup Strategy**: Backup important fetched content
- **Security First**: Scan and validate all downloaded content

### Integration Best Practices
- **Pipeline Design**: Design efficient content processing pipelines
- **Error Handling**: Handle errors gracefully at each stage
- **Monitoring**: Monitor system health and performance
- **Documentation**: Document source configurations and processes
- **Testing**: Test discovery and fetching with various source types

## Future Enhancements

### Planned Features
- **AI-Powered Discovery**: Use AI to find more relevant sources
- **Real-time Updates**: Continuous monitoring of source updates
- **Advanced Filtering**: More sophisticated content filtering
- **Social Integration**: Integration with social media platforms
- **Mobile Support**: Mobile app and responsive design sources

### Extension Points
- **Custom Source Types**: Plugin system for new source types
- **Custom Filters**: User-defined content filtering rules
- **Integration APIs**: APIs for external tool integration
- **Export Formats**: Support for additional content export formats
- **Workflow Automation**: Automated content collection workflows

This content collection system provides a robust foundation for gathering diverse content sources that feed into the SimFlo RAG pipeline, enabling comprehensive knowledge base creation and maintenance.