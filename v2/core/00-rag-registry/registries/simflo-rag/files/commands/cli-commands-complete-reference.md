# CLI Commands - Complete Reference

## Purpose
Comprehensive reference to all SimFlo RAG v2 CLI commands, organized by component with usage examples, parameters, and integration patterns. This reference covers the complete CLI interface for the system.

## Command System Overview

### Architecture
SimFlo RAG v2 implements a CLI-first architecture where all component communication uses structured Python CLI calls with JSON output:

```
Component A (CLI) → Component B (CLI) → JSON Response → Component A
```

### Command Categories
1. **Registry Commands** (`00-rag-registry`): Database management and search
2. **MCP Server Commands** (`01-mcp-server`): AI assistant integration (18 commands)
3. **RAG Builder Commands** (`02-rag-builder`): Pipeline orchestration
4. **Content Collection Commands** (`03-content-collection`): Source discovery and fetching
5. **Extractor Commands** (`04-extractors`): Content extraction (11 extractors)

### Command Aliases System
Setup: `source v2/commands.sh` enables convenient aliases:

```bash
# Registry Commands (Working)
rag_registry list
rag_registry_info --name shadcn
rag_registry_search --query "button" --limit 5
rag_registry_status
rag_registry_clean --registry shadcn
rag_registry_rebuild --registry shadcn

# MCP Server Commands (Working) - 18 commands total
mcp_search "button" --limit 10
mcp_get_component dialog --registry shadcn
mcp_list_components --type ui --platform reactjs --limit 20
mcp_set_context reactjs --session-id abc123
mcp_list_registries

# Content Collection Commands (Working)
content_discover --query "react components" --source-type github --limit 10
content_list_source_types
content_status

# Extractor Commands (Working)
extractors_list
extractors_run shadcn
extractors_run gluestack
extractors_run_all
extractors_status
```

## Registry Commands (00-rag-registry)

### Core Registry Management

#### list - List all available registries
```bash
# Full command
python3 v2/core/00-rag-registry/registry.py list --format json

# Alias
rag_registry list

# Table output
rag_registry list --format table
```

**Output**:
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
        "total_source_files": 15,
        "status": "active"
      }
    ]
  }
}
```

#### info - Get detailed registry information
```bash
# Full command
python3 v2/core/00-rag-registry/registry.py info --name shadcn --format json

# Alias
rag_registry_info --name shadcn

# Table output
rag_registry_info --name shadcn --format table
```

**Parameters**:
- `--name`: Registry name (required)

**Output**:
```json
{
  "success": true,
  "timestamp": "2025-09-30T21:37:01.043963",
  "data": {
    "name": "shadcn",
    "path": "/path/to/registries/shadcn",
    "database_path": "/path/to/registries/shadcn/chroma_db",
    "files_path": "/path/to/registries/shadcn/files",
    "db_exists": true,
    "files_exist": true,
    "total_db_files": 12,
    "total_source_files": 15,
    "last_updated": "2025-09-30T20:00:00Z",
    "collection_count": 1,
    "document_count": 156,
    "status": "active"
  }
}
```

#### search - Search across all registries
```bash
# Full command
python3 v2/core/00-rag-registry/registry.py search --query "button component" --limit 10 --format json

# Alias
rag_registry_search --query "button" --limit 5

# Search with limit
rag_registry_search --query "form input" --limit 15 --format table
```

**Parameters**:
- `--query`: Search query (required)
- `--limit`: Maximum results (default: 10)
- `--format`: Output format (json, table)

**Output**:
```json
{
  "success": true,
  "timestamp": "2025-09-30T21:37:01.043963",
  "data": {
    "query": "button component",
    "total_found": 25,
    "results": [
      {
        "name": "button",
        "registry": "shadcn",
        "type": "component",
        "description": "Accessible button component with variants",
        "relevance_score": 0.95,
        "source_file": "files/components/button.md"
      }
    ]
  }
}
```

#### status - Get overall system status
```bash
# Full command
python3 v2/core/00-rag-registry/registry.py status --format json

# Alias
rag_registry_status

# Detailed status
rag_registry_status --detailed --format table
```

**Output**:
```json
{
  "success": true,
  "timestamp": "2025-09-30T21:37:01.043963",
  "data": {
    "system_status": "operational",
    "total_registries": 3,
    "active_registries": 3,
    "total_documents": 156,
    "total_size": "45.2MB",
    "last_updated": "2025-09-30T20:00:00Z",
    "available_storage": "1.2GB"
  }
}
```

### Database Management Commands

#### clean-db - Clean registry database
```bash
# Full command
python3 v2/core/00-rag-registry/registry.py clean-db --registry shadcn --format json

# Alias
rag_registry_clean --registry shadcn
```

**Parameters**:
- `--registry`: Registry name (required)

#### clean-all - Clean registry database and files
```bash
# Full command
python3 v2/core/00-rag-registry/registry.py clean-all --registry shadcn --format json

# Alias
rag_registry_clean_all --registry shadcn
```

**Parameters**:
- `--registry`: Registry name (required)

#### rebuild-db - Rebuild registry database
```bash
# Full command
python3 v2/core/00-rag-registry/registry.py rebuild-db --registry shadcn --format json

# Alias
rag_registry_rebuild --registry shadcn
```

**Parameters**:
- `--registry`: Registry name (required)

## MCP Server Commands (01-mcp-server)

### Component Search & Discovery

#### search - Search for components
```bash
# Full command
python3 v2/core/01-mcp-server/mcp_server.py search "button" --limit 10 --platform reactjs --format json

# Alias
mcp_search "button" --limit 10

# Platform-specific search
mcp_search "modal dialog" --platform reactjs --limit 5

# Natural language search
mcp_search "form with validation and submit button" --limit 10
```

**Parameters**:
- `query`: Search query (required)
- `--limit`: Maximum results (default: 10)
- `--platform`: Platform filter (reactjs, react-native)
- `--format`: Output format (json, table)

**Output**:
```json
{
  "success": true,
  "timestamp": "2025-09-30T21:37:55.806146",
  "data": {
    "query": "button",
    "platform": "reactjs",
    "total_found": 3,
    "components": [
      {
        "name": "button",
        "type": "component",
        "registry": "shadcn",
        "relevance_score": 0.95,
        "platform_relevance": 1.0,
        "description": "Accessible button component with variants"
      }
    ]
  }
}
```

#### get-component - Get component details
```bash
# Full command
python3 v2/core/01-mcp-server/mcp_server.py get-component button --registry shadcn --format json

# Alias
mcp_get_component button

# From specific registry
mcp_get_component dialog --registry shadcn

# Table output
mcp_get_component input --format table
```

**Parameters**:
- `component_name`: Component name (required)
- `--registry`: Registry name (optional)
- `--format`: Output format (json, table)

**Output**:
```json
{
  "success": true,
  "timestamp": "2025-09-30T21:37:01.043963",
  "data": {
    "name": "button",
    "type": "component",
    "description": "Accessible button component with multiple variants",
    "registry": "shadcn",
    "platform": ["reactjs"],
    "dependencies": ["@radix-ui/react-slot"],
    "install_command": "npx shadcn-ui@latest add button",
    "usage_examples": [
      "import { Button } from \"@/components/ui/button\"",
      "<Button>Click me</Button>"
    ]
  }
}
```

#### list-components - List available components
```bash
# Full command
python3 v2/core/01-mcp-server/mcp_server.py list-components --type ui --platform reactjs --limit 20 --format json

# Alias
mcp_list_components --type ui --platform reactjs --limit 20

# List all components
mcp_list_components --limit 50

# By type only
mcp_list_components --type hooks --limit 30
```

**Parameters**:
- `--type`: Component type (ui, hooks, blocks)
- `--platform`: Platform filter (reactjs, react-native)
- `--limit`: Maximum results
- `--format`: Output format

### Context Management

#### set-context - Set platform context
```bash
# Full command
python3 v2/core/01-mcp-server/mcp_server.py set-context reactjs --session-id abc123 --format json

# Alias
mcp_set_context reactjs --session-id abc123

# With project info
mcp_set_context reactnative --session-id mobile-app --project-type "dashboard"

# Documentation context
mcp_set_context documentation --session-id ai-learning
```

**Parameters**:
- `platform`: Target platform (reactjs, react-native, documentation)
- `--session-id`: Session identifier
- `--project-type`: Project type (optional)
- `--format`: Output format

**Output**:
```json
{
  "success": true,
  "timestamp": "2025-09-30T21:37:01.043963",
  "data": {
    "platform": "reactjs",
    "session_id": "abc123",
    "project_type": null,
    "timestamp": 1696090621,
    "confidence": 0.95,
    "context_set": true
  }
}
```

#### get-context - Get current platform context
```bash
# Full command
python3 v2/core/01-mcp-server/mcp_server.py get-context --session-id abc123 --format json

# Alias
mcp_get_context --session-id abc123

# Current context
mcp_get_context
```

**Parameters**:
- `--session-id`: Session identifier (optional)

### Registry Management

#### list-registries - List available registries
```bash
# Full command
python3 v2/core/01-mcp-server/mcp_server.py list-registries --platform reactjs --format json

# Alias
mcp_list_registries

# Platform-specific
mcp_list_registries --platform reactjs

# Table output
mcp_list_registries --format table
```

**Parameters**:
- `--platform`: Platform filter (optional)
- `--format`: Output format

**Output**:
```json
{
  "success": true,
  "timestamp": "2025-09-30T21:37:01.043963",
  "data": {
    "total_registries": 3,
    "registries": [
      {
        "name": "shadcn",
        "path": "rag_databases/shadcn",
        "platform": ["reactjs"],
        "description": "Component registry for shadcn",
        "component_count": 80,
        "is_active": true,
        "registry_type": "component"
      }
    ]
  }
}
```

### Extraction Management Commands

#### run-extraction - Run extraction for registry
```bash
# Full command
python3 v2/core/01-mcp-server/mcp_server.py run-extraction --registry shadcn --mode test --format json

# Alias
mcp_run_extraction --registry shadcn

# Production mode
mcp_run_extraction --registry gluestack --mode production
```

**Parameters**:
- `--registry`: Registry name (required)
- `--mode`: Extraction mode (test, production)

#### extraction-status - Get extraction system status
```bash
# Full command
python3 v2/core/01-mcp-server/mcp_server.py extraction-status --format json

# Alias
mcp_extraction_status
```

**Output**:
```json
{
  "success": true,
  "timestamp": "2025-09-30T21:37:01.043963",
  "data": {
    "extraction_system": "operational",
    "available_registries": ["shadcn", "gluestack", "simflo-rag"],
    "last_extraction": "2025-09-30T20:00:00Z",
    "status": "ready",
    "supported_extractors": ["shadcn", "gluestack", "documentation"]
  }
}
```

#### list-extraction-registries - List extraction registries
```bash
# Full command
python3 v2/core/01-mcp-server/mcp_server.py list-extraction-registries --format json

# Alias
mcp_list_extraction_registries
```

#### clear-extraction-data - Clear extraction data
```bash
# Full command
python3 v2/core/01-mcp-server/mcp_server.py clear-extraction-data --registry shadcn --format json

# Alias
mcp_clear_extraction_data --registry shadcn
```

#### search-by-category - Search within categories
```bash
# Full command
python3 v2/core/01-mcp-server/mcp_server.py search-by-category "button" components --format json

# Alias
mcp_search_by_category "button" components

# Search in hooks
mcp_search_by_category "form" hooks

# Search in blocks
mcp_search_by_category "sidebar" blocks
```

**Parameters**:
- `query`: Search query (required)
- `category`: Category (components, hooks, blocks)

#### list-registry-sources - List registry sources
```bash
# Full command
python3 v2/core/01-mcp-server/mcp_server.py list-registry-sources shadcn --format json

# Alias
mcp_list_registry_sources shadcn
```

**Parameters**:
- `registry_name`: Registry name (required)

## Content Collection Commands (03-content-collection)

### Source Discovery

#### discover - Discover sources
```bash
# Full command
python3 v2/03-content-collection/content_collection_cli.py discover --query "react components" --source-type github --limit 10 --format json

# Alias
content_discover --query "react components" --source-type github --limit 10

# Different source types
content_discover --query "react hooks" --source-type npm --limit 15
content_discover --query "documentation" --source-type docs --limit 5
```

**Parameters**:
- `--query`: Search query (required)
- `--source-type`: Source type (github, npm, docs, community)
- `--limit`: Maximum results (default: 10)
- `--format`: Output format (json, table)

**Output**:
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
        "relevance_score": 0.95
      }
    ]
  }
}
```

### Content Fetching

#### fetch - Fetch content from sources
```bash
# Full command
python3 v2/03-content-collection/content_collection_cli.py fetch --sources-file sources.json --output-dir raw_content/ --format json

# Alias
content_fetch --sources-file sources.json --output-dir raw_content/

# From specific source
content_fetch --source "https://github.com/shadcn-ui/ui" --output-dir raw_content/shadcn/

# With depth control
content_fetch --sources-file sources.json --output-dir raw_content/ --depth 1
```

**Parameters**:
- `--sources-file`: JSON file with discovered sources
- `--source`: Single source URL
- `--output-dir`: Output directory (required)
- `--depth`: Fetch depth for repositories (default: 1)

### System Status

#### status - Get system status
```bash
# Full command
python3 v2/03-content-collection/content_collection_cli.py status --format json

# Alias
content_status

# Detailed status
content_status --detailed
```

#### list-source-types - List available source types
```bash
# Full command
python3 v2/03-content-collection/content_collection_cli.py list-source-types --format json

# Alias
content_list_source_types

# Detailed information
content_list_source_types --detailed
```

## Extractor Commands (04-extractors)

### Extractor Management

#### list - List available extractors
```bash
# Full command
python3 v2/04-extractors/extractors_cli.py list --format json

# Alias
extractors_list

# By category
extractors_list --category component-libraries

# Table output
extractors_list --format table
```

**Output**:
```json
{
  "success": true,
  "timestamp": "2025-09-30T21:37:01.043963",
  "data": {
    "total_extractors": 11,
    "extractors": [
      {
        "name": "shadcn",
        "description": "Extract shadcn/ui components from registry files",
        "category": "component-libraries",
        "supported_sources": ["github", "local"],
        "status": "active"
      }
    ]
  }
}
```

#### run - Run specific extractor
```bash
# Full command
python3 v2/04-extractors/extractors_cli.py run shadcn --source-type github --repository shadcn-ui/ui --output-dir extracted/shadcn/ --format json

# Alias
extractors_run shadcn

# With local source
extractors_run gluestack --source-type local --source-path /path/to/gluestack --output-dir extracted/gluestack/

# Specific repository
extractors_run shadcn --source-type github --repository my-org/shadcn-custom --output-dir extracted/custom/
```

**Parameters**:
- `extractor_name`: Extractor name (required)
- `--source-type`: Source type (github, local, api)
- `--repository`: GitHub repository (format: owner/repo)
- `--source-path`: Local source path
- `--output-dir`: Output directory (required)

#### run-all - Run all extractors
```bash
# Full command
python3 v2/04-extractors/extractors_cli.py run-all --output-dir extracted/all/ --format json

# Alias
extractors_run_all

# Specific category
extractors_run_all --category component-libraries --output-dir extracted/components/

# Parallel execution
extractors_run_all --parallel --output-dir extracted/all/
```

#### status - Get extractor system status
```bash
# Full command
python3 v2/04-extractors/extractors_cli.py status --format json

# Alias
extractors_status

# Detailed status
extractors_status --detailed

# Specific extractor
extractors_status --extractor shadcn
```

## RAG Builder Commands (02-rag-builder)

### Pipeline Management

#### status - Get pipeline status
```bash
# Full command
python3 v2/02-rag-builder/rag_builder_cli.py status --format json

# Alias
rag_builder_status
```

#### list-profiles - List available profiles
```bash
# Full command
python3 v2/02-rag-builder/rag_builder_cli.py list-profiles --format json

# Alias
rag_builder_list_profiles
```

#### check - Check system health
```bash
# Full command
python3 v2/02-rag-builder/rag_builder_cli.py check --format json

# Alias
rag_builder_check
```

## Integration Workflows

### Complete AI Assistant Workflow

```bash
# 1. Set platform context
mcp_set_context reactjs --session-id ai-session-001

# 2. Search for components
mcp_search "form with validation and submit button" --limit 5

# 3. Get component details
mcp_get_component form --registry shadcn

# 4. List related components
mcp_list_components --type ui --platform reactjs --limit 20

# 5. Check registry status
rag_registry_status
```

### Content Processing Pipeline

```bash
# 1. Discover sources
content_discover --query "react component libraries" --source-type github --limit 10

# 2. Fetch content
content_fetch --sources-file discovered_sources.json --output-dir raw_content/

# 3. Extract components
extractors_run_all --parallel --output-dir extracted/

# 4. Update registries
rag_registry_rebuild --registry shadcn
rag_registry_rebuild --registry gluestack

# 5. Verify with search
rag_registry_search --query "button component" --limit 10
```

### Development Setup Workflow

```bash
# 1. System health check
rag_builder_check
rag_registry_status
extractors_status

# 2. Content collection
content_discover --query "shadcn components" --source-type github --limit 1
content_fetch --source "https://github.com/shadcn-ui/ui" --output-dir raw_content/shadcn/

# 3. Extraction
extractors_run shadcn --source-type local --source-path raw_content/shadcn/ --output-dir extracted/shadcn/

# 4. Registry update
rag_registry_rebuild --registry shadcn

# 5. Test search functionality
mcp_search "button" --limit 5
```

## Helper Functions

### System Status and Testing

#### simflo_help - Show command reference
```bash
# Show all available commands
simflo_help

# Show specific category
simflo_help registry
simflo_help mcp
simflo_help content
simflo_help extractors
```

#### simflo_setup - Test core components
```bash
# Test all core components
simflo_setup

# Test specific component
simflo_setup registry
simflo_setup mcp
simflo_setup content
simflo_setup extractors
```

#### simflo_status - Quick status across all components
```bash
# Show status of all components
simflo_status

# Detailed status
simflo_status --detailed
```

#### simflo_test - Run core test suites
```bash
# Run all tests
simflo_test

# Run specific tests
simflo_test registry
simflo_test mcp
simflo_test content
simflo_test extractors
```

## Error Handling

### Common Error Patterns

All commands return structured error responses:

```json
{
  "success": false,
  "timestamp": "2025-09-30T21:37:01.043963",
  "error": "Registry 'unknown' not found",
  "error_code": "REGISTRY_NOT_FOUND",
  "suggestions": ["Use 'list-registries' to see available registries"]
}
```

### Troubleshooting Commands

```bash
# Check system health
simflo_status
simflo_setup

# Verify component functionality
rag_registry_status
mcp_extraction_status
extractors_status

# Test with help commands
simflo_help
rag_registry_info --help
mcp_search --help
```

## Performance Tips

1. **Use Aliases**: Enable command aliases with `source v2/commands.sh`
2. **Parallel Processing**: Use `--parallel` flags where available
3. **Format Selection**: Use `--format table` for human-readable output
4. **Batch Operations**: Use `run-all` commands instead of multiple individual runs
5. **Status Monitoring**: Regularly check system status with `simflo_status`

This comprehensive CLI reference provides complete coverage of all SimFlo RAG v2 commands, enabling effective system operation and integration for both users and AI assistants.