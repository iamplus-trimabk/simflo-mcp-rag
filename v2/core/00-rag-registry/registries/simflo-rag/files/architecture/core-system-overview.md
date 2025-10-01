# Core System Components Overview

## Purpose
Contains the essential system components that form the backbone of SimFlo RAG functionality.

## Component Architecture

### CLI Interface Philosophy
SimFlo RAG v2 follows a CLI-first architecture where all component communication uses simple Python CLI calls with JSON output formats.

### Core Components Breakdown

#### 00-rag-registry: Registry System
**Location**: `v2/core/00-rag-registry/`
**Purpose**: Central registry system for managing multiple RAG databases
**Key Features**:
- Registry-based organization with isolated databases
- CLI management commands for registry operations
- Support for multiple component libraries (shadcn, gluestack, simflo-rag)
- Database cleanup and rebuilding capabilities

**Essential CLI Commands**:
```bash
# Registry Management
python3 v2/core/00-rag-registry/registry.py list --format json
python3 v2/core/00-rag-registry/registry.py info --name shadcn --format json
python3 v2/core/00-rag-registry/registry.py search --query "button" --limit 10 --format json
python3 v2/core/00-rag-registry/registry.py status --format json

# Database Operations
python3 v2/core/00-rag-registry/registry.py clean-db --registry shadcn --format json
python3 v2/core/00-rag-registry/registry.py clean-all --registry shadcn --format json
python3 v2/core/00-rag-registry/registry.py rebuild-db --registry shadcn --format json
```

#### 01-mcp-server: AI Assistant Integration
**Location**: `v2/core/01-mcp-server/`
**Purpose**: CLI-only implementation for AI assistant integration
**Key Features**:
- Direct command-line interface for AI assistants
- 18 comprehensive commands for component search and discovery
- JSON and table output formats
- Context management for intelligent recommendations
- Integration with RAG pipeline components

**Essential CLI Commands**:
```bash
# Component Search & Discovery
python3 v2/core/01-mcp-server/mcp_server.py search "button" --limit 10 --platform reactjs --format json
python3 v2/core/01-mcp-server/mcp_server.py get-component button --registry shadcn --format json
python3 v2/core/01-mcp-server/mcp_server.py list-components --type ui --platform reactjs --limit 20 --format json

# Context Management
python3 v2/core/01-mcp-server/mcp_server.py set-context reactjs --session-id abc123 --format json
python3 v2/core/01-mcp-server/mcp_server.py get-context --session-id abc123 --format json

# Registry Management
python3 v2/core/01-mcp-server/mcp_server.py list-registries --platform reactjs --format json
```

#### 02-rag-builder: Pipeline Orchestration
**Location**: `v2/core/02-rag-builder/`
**Purpose**: Pipeline orchestration and RAG construction
**Key Features**:
- Centralized DatabaseManager for unified database operations
- Pipeline orchestration with CLI wrapper
- Vector database creation and management
- Integration with extractors and content collection

**Key Components**:
- `database_manager.py`: Centralized database management with singleton pattern
- `registry_manager.py`: Registry operations and management
- Pipeline orchestration and coordination

#### 03-content-collection: Source Discovery
**Location**: `v2/03-content-collection/`
**Purpose**: Content discovery and acquisition system
**Key Features**:
- Automated source discovery and validation
- Content fetching from various sources (GitHub, documentation sites)
- Integration with extractors for content processing
- CLI interface for automation

**Essential CLI Commands**:
```bash
# Source Discovery
python3 v2/03-content-collection/content_collection_cli.py discover --query "react components" --source-type github --limit 10 --format json
python3 v2/03-content-collection/content_collection_cli.py list-source-types --format json

# System Status
python3 v2/03-content-collection/content_collection_cli.py status --format json
```

#### 04-extractors: Content Extraction
**Location**: `v2/04-extractors/`
**Purpose**: Specialized content extraction from various sources
**Key Features**:
- 11 specialized extractors for different content types
- GitHub CLI integration for reliable repository access
- Simple and complex extractor patterns
- CLI wrapper for orchestration

**Essential CLI Commands**:
```bash
# Extractor Management
python3 v2/04-extractors/extractors_cli.py list-extractors --format json
python3 v2/04-extractors/extractors_cli.py status --format json

# Extraction Operations
python3 v2/04-extractors/extractors_cli.py run-extractor shadcn --format json
python3 v2/04-extractors/extractors_cli.py run-all-extractors --format json
```

## Integration Patterns

### Command Alias System
**Setup**: Run `source v2/commands.sh` to enable aliases

**Available Aliases**:
```bash
# Quick Status & Testing
simflo_status              # Show status of all components
simflo_test               # Run core test suites
simflo_help               # Show command reference

# Component Commands
rag_registry list         # Registry management
mcp_search "button"       # MCP server operations
content_discover --query "react"  # Content collection
extractors_list           # Extractor management
test_all                  # Run all tests
```

### CLI Output Format
All commands return structured JSON:
```json
{
  "success": true,
  "timestamp": "2025-09-30T21:37:01.043963",
  "data": {
    // Command-specific data
  }
}
```

## Testing Infrastructure

### Test Coverage
- **Registry System**: 10/10 tests passing (100%)
- **MCP Server**: 16/16 tests passing (100%)
- **Content Collection**: 8/8 tests passing (100%)
- **Extractors**: 8/8 tests passing (100%)

### Running Tests
```bash
# Run all tests
simflo_test

# Individual component tests
test_registry              # Registry system tests
test_mcp                  # MCP server tests
test_content              # Content collection tests
test_extractors           # Extractor tests
```

## Key Achievements

### Database Consolidation
- **Before**: 86+ files across 6 databases with massive duplication
- **After**: 18 files in 2 standardized databases
- **Solution**: Centralized DatabaseManager with standardized paths

### CLI-First Architecture
- All component communication via CLI interfaces
- Simple Python calls without HTTP overhead
- Consistent JSON output format across all commands
- Comprehensive command alias system

### Quality Standards
- 100% test pass rates across all components
- Comprehensive error handling and logging
- Production-ready implementations
- Evidence-based completion verification

## Benefits of Core System

1. **Simplicity**: CLI interfaces are easy to understand and debug
2. **Performance**: Direct Python calls without network overhead
3. **Reliability**: Comprehensive test coverage and error handling
4. **Maintainability**: Clear component boundaries and responsibilities
5. **Scalability**: Easy to add new registries and extractors
6. **Integration**: Seamless AI assistant integration patterns

## Usage Examples

### AI Assistant Integration Pattern
```bash
# AI assistant searches for components
python3 v2/core/01-mcp-server/mcp_server.py search "modal dialog with form validation" --platform reactjs --limit 5 --format json

# Returns structured data with component matches, relevance scores, and installation information
```

### Registry Management Pattern
```bash
# Add new component library to system
python3 v2/core/00-rag-registry/registry.py rebuild-db --registry new-library

# Search across all registries
python3 v2/core/01-mcp-server/mcp_server.py search "button component" --format json
```

### Content Pipeline Pattern
```bash
# Discover new sources
python3 v2/03-content-collection/content_collection_cli.py discover --query "react components" --source-type github

# Extract and process content
python3 v2/04-extractors/extractors_cli.py run-extractor shadcn

# Update registry with new content
python3 v2/core/00-rag-registry/registry.py rebuild-db --registry shadcn
```