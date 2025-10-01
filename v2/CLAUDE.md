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
- **00-rag-registry**: ✅ Complete - Registry-based organization with CLI management commands
- **01-mcp-server**: ✅ Complete - CLI-only architecture with 12 commands for AI assistant integration + comprehensive user guide
- **02-rag-builder**: ✅ Complete - Pipeline orchestration with CLI wrapper
- **03-content-collection**: ✅ Complete - Source discovery and content acquisition with CLI interface
- **04-extractors**: ✅ Complete - CLI wrapper with access to 11 specialized extractors for content extraction + comprehensive user guide

## CLI Examples
```bash
# RAG Registry CLI (Working) - Registry-based management
v2/core/00-rag-registry/registry.py list --format json
v2/core/00-rag-registry/registry.py info --name shadcn --format json
v2/core/00-rag-registry/registry.py search --query "button" --limit 5 --format json
v2/core/00-rag-registry/registry.py status --format json
v2/core/00-rag-registry/registry.py clean-db --registry shadcn --format json
v2/core/00-rag-registry/registry.py rebuild-db --registry shadcn --format json

# MCP Server CLI (Working) - AI Assistant Integration
v2/core/01-mcp-server/mcp_server.py search "button" --limit 10 --format json
v2/core/01-mcp-server/mcp_server.py get-component dialog --registry shadcn --format json
v2/core/01-mcp-server/mcp_server.py list-components --type ui --platform reactjs --limit 20 --format json
v2/core/01-mcp-server/mcp_server.py set-context reactjs --session-id abc123 --format json
v2/core/01-mcp-server/mcp_server.py list-registries --format json

# RAG Builder CLI (Working) - Pipeline orchestration
v2/core/02-rag-builder/rag_builder_cli.py status --format json
v2/core/02-rag-builder/rag_builder_cli.py list-profiles --format json
v2/core/02-rag-builder/rag_builder_cli.py check --format json

# Content Collection CLI (Working) - Source discovery and content acquisition
v2/03-content-collection/content_collection_cli.py discover --query "react components" --source-type github --limit 10 --format json
v2/03-content-collection/content_collection_cli.py list-source-types --format json
v2/03-content-collection/content_collection_cli.py status --format json

# Extractors CLI (Working) - Content extraction
v2/04-extractors/extractors_cli.py list-extractors --format json
v2/04-extractors/extractors_cli.py run-extractor shadcn --format json
v2/04-extractors/extractors_cli.py run-all-extractors --format json
v2/04-extractors/extractors_cli.py status --format json

# CLI Tests
v2/core/00-rag-registry/tests/run.py --verbose
v2/core/01-mcp-server/tests/run.py --verbose
v2/03-content-collection/tests/run.py --verbose
v2/04-extractors/tests/run.py --verbose
v2/tests/cmd_test_executor.py v2/core/00-rag-registry/tests/cmd_tests.json
v2/tests/cmd_test_executor.py v2/core/01-mcp-server/tests/mcp_tests.json
v2/tests/cmd_test_executor.py v2/03-content-collection/tests/content_collection_tests.json
v2/tests/cmd_test_executor.py v2/04-extractors/tests/extractor_tests.json
```
