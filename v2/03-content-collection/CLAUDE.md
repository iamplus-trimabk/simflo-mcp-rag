# Content Collection System

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
- **source-discovery/**: Automated source discovery and validation
- **content-fetching/**: Content acquisition and download tools

## Integration with Other Components

The content collection system provides source material for:
- **04-extractors**: Uses discovered sources for content extraction
- **02-rag-builder**: Processes extracted content into RAG databases
- **00-rag-registry**: Stores processed content in registry-based structure

## CLI Interface
```bash
# Discover sources for component libraries
v2/03-content-collection/content_collection_cli.py discover --query "react components" --source-type github --limit 10 --format json

# Fetch content from discovered sources
v2/03-content-collection/content_collection_cli.py fetch --sources-file sources.json --output-dir raw_content/

# Get system status
v2/03-content-collection/content_collection_cli.py status --format json

# List available source types
v2/03-content-collection/content_collection_cli.py list-source-types --format json

# Integration example
v2/03-content-collection/content_collection_cli.py discover --query "shadcn" --source-type github | \
v2/03-content-collection/content_collection_cli.py fetch --sources - --output-dir raw_content/
```

## Content Types

### Source Discovery
- **GitHub repositories**: Component library repositories
- **NPM packages**: Package metadata and documentation
- **Documentation sites**: API docs, guides, examples
- **Community resources**: Blog posts, tutorials, examples

### Content Fetching
- **Repository cloning**: Git-based content retrieval
- **Web scraping**: Documentation and guide extraction
- **API integration**: Package information retrieval
- **File downloads**: Asset and resource acquisition

## Status
✅ **Complete** - Fully implemented with CLI interface and comprehensive testing

This component provides source discovery and content acquisition capabilities that feed into the RAG pipeline.

## Implementation Details

This component provides:
1. Integration with existing extractors in 04-extractors
2. Content feeding to 02-rag-builder for processing
3. Support for multiple content sources and formats
4. CLI interfaces for automation
5. Error recovery and retry logic
