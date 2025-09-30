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
core/registry-system/registry.py info --name shadcn_db --format json
core/registry-system/registry.py search --query "button" --limit 10 --format json
core/registry-system/registry.py status --format json
```

## Registry System CLI
The registry system provides a CLI interface for managing and searching multiple RAG databases.

### Commands
- **list**: List all available registries
- **info**: Get information about a specific registry
- **search**: Search across all registries for components
- **status**: Get system status and statistics

### Output Formats
All commands support `--format json` (default) and `--format table` output formats.

### Examples
```bash
# List all registries
python3 core/registry-system/registry.py list --format json

# Get registry information
python3 core/registry-system/registry.py info --name shadcn_db --format json

# Search for components
python3 core/registry-system/registry.py search --query "button" --limit 5 --format json

# Get system status
python3 core/registry-system/registry.py status --format json
```
