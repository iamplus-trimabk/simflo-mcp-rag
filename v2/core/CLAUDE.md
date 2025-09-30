# Core System Components

## Purpose
Contains the essential system components that form the backbone of simflo-rag's functionality.

## Role in System
The **execution engine** of simflo-rag, providing MCP protocol services, RAG capabilities, and registry management.

## What This Directory Contains
- **mcp-server/**: MCP protocol server implementation
- **rag-engine/**: RAG construction, search, and management
- **registry-system/**: Central registry coordination and metadata

## What This Directory Should NOT Contain
- **Extractors** - belong in extractors/ directory
- **Content collection logic** - belongs in content-collection/
- **Testing code** - belongs in testing/ directory
- **Configuration files** - belongs in configuration/ directory
- **Utility functions** - belongs in utilities/ directory

## CLI Interface
```bash
# MCP Server operations
core/mcp-server/server.py start --port 8080
core/mcp-server/server.py stop --pid-file /path/to/pid
core/mcp-server/server.py status --format json

# RAG Engine operations
core/rag-engine/builder.py build --config /path/to/config --output /path/to/output
core/rag-engine/search.py query --index rag-index --query "search terms"
core/rag-engine/vector-store.py create --name vector-store --dimension 1536

# Registry System operations
core/registry-system/registry-manager.py list --format json
core/registry-system/registry-manager.py add --name registry --path /path/to/registry
core/registry-system/registry-manager.py validate --name registry
```

## Dependencies and Relationships
- **Uses**: utilities/ for common functions
- **Provides**: CLI interfaces for all core functionality
- **Integrates with**: extractors/, content-collection/, data-management/
- **Serves**: All other components through CLI interfaces

## Implementation Guidelines
1. **CLI-first design** - all functionality exposed as CLI commands
2. **JSON I/O** - standard format for data exchange
3. **Error handling** - consistent exit codes and error messages
4. **Isolation** - components should work independently
5. **State management** - minimal state, prefer external storage