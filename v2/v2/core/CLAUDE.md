# Core System Components

## Purpose
Contains the essential system components that form the backbone of simflo-rag functionality.

## Components
- **mcp-server/**: MCP protocol server implementation
- **rag-engine/**: RAG construction, search, and management  
- **registry-system/**: Central registry coordination and metadata

## CLI Interface
```bash
core/mcp-server/server.py start --port 8080
core/rag-engine/builder.py build --config config.json
core/registry-system/registry.py list --format json
```
