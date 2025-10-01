# RAG Registry System

## Purpose
Central registry system for managing multiple RAG databases with registry-based organization. Each registry (shadcn, gluestack, community) has its own folder with vector databases and source files organized by extractor type.

## Architecture
Registry-based structure where each component library has its own dedicated registry:
```
registries/
├── shadcn/
│   ├── db/           # Vector databases for shadcn components
│   └── files/        # Source files organized by extractor type
│       ├── components/
│       ├── hooks/
│       └── blocks/
├── gluestack/
│   ├── db/           # Vector databases for gluestack components
│   └── files/        # Source files organized by extractor type
│       ├── components/
│       ├── hooks/
│       └── blocks/
└── community/
    ├── db/           # Vector databases for community components
    └── files/        # Source files from various community sources
```

## Registry Management

### CLI Commands
```bash
# List all registries
python3 registry.py list --format json

# Get registry information
python3 registry.py info --name shadcn --format json

# Search across registries
python3 registry.py search --query "button" --limit 10 --format json

# Get system status
python3 registry.py status --format json

# Clean specific registry database
python3 registry.py clean-db --registry shadcn --format json

# Clean registry database and files
python3 registry.py clean-all --registry shadcn --format json

# Rebuild registry database from files
python3 registry.py rebuild-db --registry shadcn --format json
```

### Registry Operations

#### Database Management
- **clean-db**: Remove vector database for a specific registry
- **clean-all**: Remove both database and source files for a registry
- **rebuild-db**: Reconstruct vector database from source files

#### File Organization
Source files are organized by extractor type within each registry:
- **components/**: Component definitions and examples
- **hooks/**: Custom hooks and utilities
- **blocks/**: Block components and layouts
- **documentation/**: Documentation files and guides

## Integration with RAG Pipeline

The registry system integrates with:
- **Extractors**: Content is organized by extractor type
- **RAG Builder**: Uses registry databases for vector search
- **MCP Server**: Provides AI assistant access to registry content

## Benefits

1. **Isolation**: Each registry is completely independent
2. **Scalability**: Easy to add new registries for different component libraries
3. **Organization**: Clear separation of databases and source files
4. **Management**: CLI commands for registry maintenance
5. **Flexibility**: Support for different extractor types and content sources