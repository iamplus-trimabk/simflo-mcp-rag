# simflo-rag v2 - Restructured Architecture

## Purpose
This directory contains the holistically restructured architecture for simflo-rag, designed for long-term maintainability and evolutionary development.

## Components (Numbered System)
- **00-rag-registry/**: Registry-based RAG database management with CLI commands
- **01-mcp-server/**: AI assistant integration via CLI (12 commands)
- **02-rag-builder/**: Pipeline orchestration and RAG construction
- **03-content-collection/**: Source discovery and content acquisition (documentation only)
- **04-extractors/**: Content extraction from various sources (11 specialized extractors)

## CLI-First Architecture
All component-to-component communication uses CLI interfaces with simple Python CLI calls.

## Implementation Guidelines
- CLI interfaces for all component communication
- Documentation first - every directory has CLAUDE.md
- Clear boundaries between components
- Evolutionary development approach
- JSON output format for all CLI commands
- Registry-based organization for RAG databases

## Completed Components
- **00-rag-registry**: ✅ Complete - Registry-based organization with CLI management commands (shadcn + gluestack only)
- **01-mcp-server**: ✅ Complete - CLI-only architecture with 18 commands for AI assistant integration + comprehensive user guide
- **02-rag-builder**: ✅ Complete - Pipeline orchestration with CLI wrapper
- **03-content-collection**: ✅ Complete - Source discovery and content acquisition with CLI interface
- **04-extractors**: ✅ Complete - CLI wrapper with 2 opinionated extractors (shadcn + gluestack) using GitHub CLI

## Command Alias System

**Setup**: Run `source v2/commands.sh` to enable aliases, or add to shell profile for persistence.

### Helper Functions
- `simflo_help` - Show command reference
- `simflo_setup` - Test core components functionality
- `simflo_status` - Quick status across all components
- `simflo_test` - Run core test suites

## CLI Examples (Using Command Aliases)

```bash
# Quick Status & Testing
simflo_status              # Show status of all components
simflo_test               # Run core test suites
simflo_help               # Show command reference

# RAG Registry CLI (Working) - Registry-based management
rag_registry list
rag_registry_info --name shadcn
rag_registry_search --query "button" --limit 5
rag_registry_status
rag_registry_clean --registry shadcn
rag_registry_rebuild --registry shadcn

# MCP Server CLI (Working) - AI Assistant Integration (18 commands total)
mcp_search "button" --limit 10
mcp_get_component dialog --registry shadcn
mcp_list_components --type ui --platform reactjs --limit 20
mcp_set_context reactjs --session-id abc123
mcp_list_registries

# MCP Server Extraction Commands (NEWLY IMPLEMENTED!)
mcp_run_extraction --registry shadcn
mcp_extraction_status
mcp_list_extraction_registries
mcp_clear_extraction_data --registry shadcn
mcp_search_by_category "button" components
mcp_list_registry_sources shadcn

# RAG Builder CLI (Working) - Pipeline orchestration
rag_builder_status
rag_builder_list_profiles
rag_builder_check

# Content Collection CLI (Working) - Source discovery and content acquisition
content_discover --query "react components" --source-type github --limit 10
content_list_source_types
content_status

# Extractors CLI (Working) - Content extraction (GitHub CLI + opinionated)
extractors_list
extractors_run shadcn
extractors_run gluestack
extractors_run_all
extractors_status

# Individual Test Commands
test_registry              # Registry system tests
test_mcp                  # MCP server tests
test_content              # Content collection tests
test_extractors           # Extractor tests
test_all                  # Run all tests
```

## Opinionated Approach

SimFlo RAG v2 takes an opinionated approach to component library support:

### Supported Libraries (Only)
- **shadcn**: Modern React component library with Radix UI primitives
- **gluestack**: Cross-platform component library (React + React Native)

### Key Features
- **GitHub CLI Integration**: Uses `gh` command for reliable repository access
- **Local-First**: Repositories downloaded to `$CONTENT_ROOT/github/{repo-name}`
- **No Sample Data**: Only real component data from actual repositories
- **Environment Variables**: Uses `$CONTENT_ROOT` for configurable paths

### Excluded Libraries
- radix-ui, mui, ant-design, and others are intentionally not supported
- This opinionated approach ensures focused, high-quality support for the selected libraries
