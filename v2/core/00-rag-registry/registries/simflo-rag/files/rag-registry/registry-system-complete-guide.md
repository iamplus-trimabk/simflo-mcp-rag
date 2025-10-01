# RAG Registry System - Complete Guide

## Purpose
Central registry system for managing multiple RAG databases with registry-based organization. Each registry has its own folder with vector databases and source files organized by extractor type.

## Architecture Overview

### Registry-Based Structure
```
registries/
├── shadcn/
│   ├── chroma_db/           # Vector database for shadcn components
│   └── files/              # Source files organized by type
│       └── components/     # Component definitions and examples
├── gluestack/
│   ├── chroma_db/           # Vector database for gluestack components
│   └── files/              # Source files organized by type
│       └── components/     # Component definitions and examples
└── simflo-rag/             # NEW: Self-documenting registry
    ├── chroma_db/           # Vector database for SimFlo RAG documentation
    └── files/              # Documentation organized by category
        ├── architecture/   # System architecture documentation
        ├── rag-registry/   # Registry system documentation
        ├── mcp-server/     # AI assistant integration docs
        ├── commands/       # CLI command references
        └── user-guides/    # Usage guides and patterns
```

## Core Components

### DatabaseManager (`database_manager.py`)
**Purpose**: Centralized manager for all ChromaDB operations
**Key Features**:
- Single source of truth for database operations
- Standardized database paths: `{registry}/chroma_db/`
- Database creation, rebuilding, and cleanup
- Singleton pattern for global access

**Key Methods**:
- `create_database()`: Create database from source files
- `rebuild_database()`: Reconstruct database from source files
- `get_database_client()`: Get ChromaDB client for operations
- `cleanup_duplicate_databases()`: Remove duplicate database files
- `get_database_stats()`: Get database statistics

### RegistryManager (`registry.py`)
**Purpose**: CLI interface for registry management
**Key Features**:
- Registry listing and information retrieval
- Database search and management operations
- Integration with centralized DatabaseManager
- Structured JSON output for all operations

## CLI Commands Reference

### Registry Information Commands
```bash
# List all available registries
python3 v2/core/00-rag-registry/registry.py list --format json

# Get detailed information about specific registry
python3 v2/core/00-rag-registry/registry.py info --name shadcn --format json

# Get overall system status
python3 v2/core/00-rag-registry/registry.py status --format json
```

**Output Format**:
```json
{
  "success": true,
  "timestamp": "2025-09-30T21:37:01.043963",
  "data": {
    "total_registries": 3,
    "registries": [
      {
        "name": "shadcn",
        "path": "/path/to/registries/shadcn",
        "db_exists": true,
        "files_exist": true,
        "total_db_files": 12,
        "total_source_files": 15
      }
    ]
  }
}
```

### Search Commands
```bash
# Search across all registries
python3 v2/core/00-rag-registry/registry.py search --query "button component" --limit 10 --format json
```

### Database Management Commands
```bash
# Clean database files for specific registry
python3 v2/core/00-rag-registry/registry.py clean-db --registry shadcn --format json

# Clean both database and source files for registry
python3 v2/core/00-rag-registry/registry.py clean-all --registry shadcn --format json

# Rebuild registry database from source files
python3 v2/core/00-rag-registry/registry.py rebuild-db --registry shadcn --format json
```

**Rebuild Database Output**:
```json
{
  "success": true,
  "timestamp": "2025-09-30T21:37:01.043963",
  "data": {
    "registry": "shadcn",
    "database_path": "/path/to/registries/shadcn/chroma_db",
    "collection_name": "components",
    "documents_processed": 25,
    "message": "Successfully rebuilt database with 25 documents"
  }
}
```

## Registry Operations

### Database Creation Process
1. **Source Files Collection**: Gather markdown files from registry's `files/` directory
2. **Document Processing**: Parse and extract content from source files
3. **Vector Database Creation**: Create ChromaDB with standardized structure
4. **Metadata Generation**: Add metadata for search and retrieval
5. **Marker File Creation**: Create database marker for tracking

### File Organization
Source files are organized by category within each registry:
- **components/**: Component definitions, examples, and usage
- **architecture/**: System architecture and design documentation
- **commands/**: CLI command references and examples
- **user-guides/**: Usage guides and integration patterns
- **setup/**: Setup and configuration documentation

### Database Standardization
- **Path Structure**: `{registry}/chroma_db/`
- **Collection Name**: `components` (standardized across registries)
- **Document IDs**: `{registry}_{document_name}` format
- **Metadata Schema**: Consistent metadata fields across all registries

## Integration with RAG Pipeline

### Content Flow
1. **Content Collection**: `03-content-collection` discovers and fetches sources
2. **Extraction**: `04-extractors` processes and extracts content
3. **Registry Population**: Content organized in registry `files/` directories
4. **Database Creation**: `registry.py rebuild-db` creates vector database
5. **Search & Retrieval**: `01-mcp-server` provides search capabilities

### MCP Server Integration
The registry system integrates with MCP server for AI assistant access:
```bash
# AI assistant searches across all registries
python3 v2/core/01-mcp-server/mcp_server.py search "react button component" --format json

# List available registries
python3 v2/core/01-mcp-server/mcp_server.py list-registries --format json
```

## Testing and Validation

### Test Suite
Run comprehensive registry system tests:
```bash
# Run all registry system tests
python3 v2/core/00-rag-registry/tests/run.py --verbose

# Run specific test file
python3 v2/tests/cmd_test_executor.py v2/core/00-rag-registry/tests/cmd_tests.json
```

### Test Coverage
- **Total tests**: 10 essential test cases
- **Pass rate**: 100% (10/10 tests passing)
- **Coverage areas**:
  - Basic functionality (list, info, search, status)
  - Output formats (JSON and table)
  - Error handling (invalid arguments, missing parameters)
  - Help commands and edge cases

## Database Management Best Practices

### Adding New Registry
1. **Create Registry Directory**: `registries/new-registry/`
2. **Organize Source Files**: Place content in appropriate subdirectories
3. **Rebuild Database**: `python3 registry.py rebuild-db --registry new-registry`
4. **Verify Integration**: Test search functionality

### Database Maintenance
- **Regular Cleanup**: Use `clean-db` to remove corrupted databases
- **Rebuilding**: Use `rebuild-db` when source files change
- **Monitoring**: Use `status` command to monitor system health

### Performance Optimization
- **Standardized Paths**: Consistent database structure improves performance
- **Singleton DatabaseManager**: Reduces database connection overhead
- **Batch Processing**: Process multiple documents efficiently

## Error Handling and Troubleshooting

### Common Issues
1. **Database Corruption**: Use `rebuild-db` to recreate from source files
2. **Missing Source Files**: Verify files exist in registry's `files/` directory
3. **Import Errors**: Check Python path and dependencies
4. **Permission Issues**: Ensure write access to registry directories

### Error Response Format
```json
{
  "success": false,
  "timestamp": "2025-09-30T21:37:01.043963",
  "data": {
    "error": "Registry 'unknown' not found"
  }
}
```

## Benefits of Registry System

1. **Isolation**: Each registry is completely independent
2. **Scalability**: Easy to add new registries for different content types
3. **Organization**: Clear separation of databases and source files
4. **Management**: Comprehensive CLI commands for maintenance
5. **Flexibility**: Support for different content types and sources
6. **Search**: Integrated vector search across all registries
7. **Self-Documenting**: System can document itself through registries

## Future Enhancements

### Planned Features
- **Registry Templates**: Standardized templates for new registries
- **Automated Updates**: Scheduled database rebuilding
- **Advanced Search**: Enhanced search with filtering and ranking
- **Multi-tenant Support**: Isolated registries for different users

### Extension Points
- **Custom Extractors**: Specialized content extraction for new sources
- **Alternative Databases**: Support for other vector databases
- **Advanced Metadata**: Custom metadata schemas for specialized use cases