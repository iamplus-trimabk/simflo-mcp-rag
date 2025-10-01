# AI Assistant Integration Guide

## Quick Start for AI Assistants

This guide provides essential information for AI assistants to discover and use SimFlo RAG functionality.

## Available Commands

### Core Commands

#### Component Search
```bash
# Search for components
python3 v2/core/01-mcp-server/mcp_server.py search "button" --limit 10

# Get specific component details
python3 v2/core/01-mcp-server/mcp_server.py get-component button --registry shadcn

# List available components
python3 v2/core/01-mcp-server/mcp_server.py list-components --type ui --platform reactjs
```

#### Registry Management
```bash
# List all registries
python3 v2/core/00-rag-registry/registry.py list

# Get registry info
python3 v2/core/00-rag-registry/registry.py info --name shadcn

# Search components across registries
python3 v2/core/00-rag-registry/registry.py search --query "dialog" --limit 5
```

#### Content Extraction
```bash
# Run extraction for specific library
python3 v2/04-extractors/extractors_cli.py run-extractor shadcn

# Run all extractors
python3 v2/04-extractors/extractors_cli.py run-all-extractors

# List available extractors
python3 v2/04-extractors/extractors_cli.py list-extractors
```

## Supported Libraries

### shadcn
- **Description**: Modern React component library with Radix UI primitives
- **Repository**: shadcn-ui/ui
- **Platform**: React
- **Installation**: Components install via npm with @radix-ui dependencies

### gluestack
- **Description**: Cross-platform component library (React + React Native)
- **Repository**: gluestack/gluestack-ui
- **Platforms**: React, React Native
- **Installation**: Components install via @gluestack-ui packages

## Integration Patterns

### Basic Component Discovery
1. Search for components using natural language queries
2. Get detailed component information including installation and usage
3. Extract installation commands and code examples
4. Provide users with working implementation code

### Extraction Workflow
1. Run extraction to update component database
2. Search newly extracted components
3. Use registry commands to manage component data

### Error Handling
- All commands return JSON with `success`, `timestamp`, and `data` fields
- Check `success` field before processing results
- Handle missing repositories gracefully

## Command Aliases

Use command aliases for easier integration:
```bash
# After sourcing v2/commands.sh
mcp_search "button"
mcp_get_component dialog --registry shadcn
extractors_run shadcn
rag_registry_search --query "input"
```

## Environment Setup

- **CONTENT_ROOT**: `/Users/tbardale/v2/simflo-mcp-rag/content` (configurable)
- **GitHub CLI**: Required for repository access (`gh` command)
- **Python 3.12+**: Required for all CLI operations

## Output Format

All commands return structured JSON:
```json
{
  "success": true,
  "timestamp": "2025-10-01T22:55:00.000000",
  "data": {
    // Command-specific data
  }
}
```

## Tips for AI Assistants

1. **Always use natural language** for component searches
2. **Check success status** before processing results
3. **Handle both shadcn and gluestack** libraries in responses
4. **Use extraction commands** to get the latest component data
5. **Provide complete code examples** with proper imports

## Common Workflows

### Finding a Button Component
```bash
# 1. Search for buttons
mcp_search "button" --limit 5

# 2. Get specific component details
mcp_get_component button --registry shadcn

# 3. Extract latest data if needed
extractors_run shadcn
```

### Setting Up Context
```bash
# Set React context for better recommendations
mcp_set_context reactjs

# View current context
mcp_get_context
```

This is sufficient information for AI assistants to discover and use SimFlo RAG functionality effectively.