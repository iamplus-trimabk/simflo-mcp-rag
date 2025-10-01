# SimFlo RAG v2 - Complete Architecture Overview

## Purpose
This directory contains the holistically restructured architecture for SimFlo RAG, designed for long-term maintainability and evolutionary development.

## System Overview
SimFlo RAG v2 is a CLI-first RAG (Retrieval-Augmented Generation) system that enables AI assistants to access and search component libraries and documentation through vector databases.

## Components (Numbered System)

### 00-rag-registry/**: Registry-based RAG database management
- **Purpose**: Central registry system for managing multiple RAG databases
- **Key Features**:
  - Registry-based organization with isolated databases
  - CLI management commands (list, info, search, rebuild, clean)
  - Support for multiple component libraries (shadcn, gluestack, simflo-rag)
- **CLI Commands**: `rag_registry list`, `rag_registry_info`, `rag_registry_search`, `rag_registry_rebuild`

### 01-mcp-server/**: AI assistant integration via CLI
- **Purpose**: CLI-only implementation providing direct command-line interface for AI assistants
- **Key Features**:
  - 18 comprehensive commands for component search and discovery
  - JSON and table output formats
  - Context management for intelligent recommendations
  - Integration with RAG pipeline components
- **CLI Commands**: `mcp_search`, `mcp_get_component`, `mcp_list_components`, `mcp_set_context`

### 02-rag-builder/**: Pipeline orchestration and RAG construction
- **Purpose**: Pipeline orchestration for building and managing RAG databases
- **Key Features**:
  - Centralized DatabaseManager for unified database operations
  - Pipeline orchestration with CLI wrapper
  - Vector database creation and management
- **Status**: Complete with centralized database management

### 03-content-collection/**: Source discovery and content acquisition
- **Purpose**: Content discovery and acquisition system for gathering information from various sources
- **Key Features**:
  - Automated source discovery and validation
  - Content fetching from GitHub repositories, documentation sites
  - Integration with extractors for content processing
- **CLI Commands**: `content_discover`, `content_list_source_types`, `content_status`

### 04-extractors/**: Content extraction from various sources
- **Purpose**: Specialized content extraction from component libraries and documentation
- **Key Features**:
  - 11 specialized extractors for different content types
  - GitHub CLI integration for reliable repository access
  - Simple and complex extractor patterns
- **CLI Commands**: `extractors_list`, `extractors_run`, `extractors_status`

## CLI-First Architecture Principles

### Design Philosophy
- **Component Communication**: All component-to-component communication uses CLI interfaces
- **Simple Python Calls**: Direct Python CLI calls without HTTP overhead
- **JSON Output Format**: Structured JSON responses for all commands
- **Registry-based Organization**: Clear separation of databases and source files

### Command Alias System
**Setup**: Run `source v2/commands.sh` to enable aliases

### Core CLI Commands
```bash
# Registry Management
rag_registry list                    # List all registries
rag_registry_info --name shadcn      # Get registry information
rag_registry_search --query "button" # Search across registries
rag_registry_rebuild --registry shadcn # Rebuild registry database

# MCP Server (AI Assistant Integration)
mcp_search "button" --limit 10       # Search components
mcp_get_component dialog --registry shadcn # Get component details
mcp_list_components --type ui        # List available components
mcp_set_context reactjs              # Set platform context

# Content Collection
content_discover --query "react"     # Discover sources
content_status                       # Get system status

# Extractors
extractors_list                      # List available extractors
extractors_run shadcn               # Run specific extractor
extractors_status                    # Get system status
```

## Implementation Status

### Completed Components ✅
- **00-rag-registry**: Registry-based organization with CLI management
- **01-mcp-server**: CLI-only architecture with 18 commands
- **02-rag-builder**: Pipeline orchestration with centralized DatabaseManager
- **03-content-collection**: Source discovery with CLI interface
- **04-extractors**: CLI wrapper with specialized extractors

### Key Achievements
- **Database Consolidation**: Eliminated 86+ duplicate files to 18 standardized files
- **Centralized Management**: Single DatabaseManager for all database operations
- **100% Test Coverage**: Registry CLI (10/10 tests), MCP Server (16/16 tests)
- **CLI-first Architecture**: All components communicate via CLI interfaces

## Opinionated Approach

### Supported Libraries (Current)
- **shadcn**: Modern React component library with Radix UI primitives
- **gluestack**: Cross-platform component library (React + React Native)
- **simflo-rag**: Self-documenting system (NEW)

### Key Features
- **GitHub CLI Integration**: Uses `gh` command for reliable repository access
- **Local-First**: Repositories downloaded to `$CONTENT_ROOT/github/{repo-name}`
- **No Sample Data**: Only real component data from actual repositories
- **Environment Variables**: Uses `$CONTENT_ROOT` for configurable paths

## Integration Patterns

### AI Assistant Integration
AI assistants can use SimFlo RAG CLI directly:
```bash
# Example AI assistant workflow
python3 v2/core/01-mcp-server/mcp_server.py search "modal dialog with form validation" --platform reactjs --limit 5 --format json
```

### Registry Management
```bash
# Add new registry
python3 v2/core/00-rag-registry/registry.py rebuild-db --registry new-library

# Search across all registries
python3 v2/core/01-mcp-server/mcp_server.py search "button component" --format json
```

### Content Pipeline
```bash
# Discover new sources
python3 v2/03-content-collection/content_collection_cli.py discover --query "react components"

# Extract content
python3 v2/04-extractors/extractors_cli.py run-extractor shadcn

# Rebuild registry
python3 v2/core/00-rag-registry/registry.py rebuild-db --registry shadcn
```

## Benefits of v2 Architecture

1. **Maintainability**: Clear component boundaries and CLI interfaces
2. **Scalability**: Easy to add new registries and extractors
3. **Reliability**: Comprehensive test coverage and error handling
4. **Performance**: Direct CLI calls without HTTP overhead
5. **Flexibility**: Support for multiple content sources and formats
6. **Self-Documenting**: System documents itself through simflo-rag registry

## Future Roadmap

### v4 Implementation Requirements
- Complex extractors (shadcn_components_extractor.py, shadcn_hooks_extractor.py, shadcn_blocks_extractor.py, gluestack_extractor.py) marked for v4.0+ implementation
- Current simple extractors (shadcn_extractor.py, gluestack_extractor_simple.py) provide sufficient functionality

### Extension Points
- New registries for additional component libraries
- Enhanced extractors for specialized content types
- Advanced AI assistant integration patterns
- Performance optimization and caching