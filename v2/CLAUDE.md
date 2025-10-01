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

## CLI Examples (Using Command Aliases)

**Setup**: First run `source commands.sh` to enable aliases, or add to your shell profile for persistence.
```bash
# RAG Registry CLI (Working) - Registry-based management
rag_registry list --format json
rag_registry info --name shadcn --format json
rag_registry search --query "button" --limit 5 --format json
rag_registry status --format json
rag_registry clean-db --registry shadcn --format json
rag_registry rebuild-db --registry shadcn --format json

# MCP Server CLI (Working) - AI Assistant Integration
mcp_server search "button" --limit 10 --format json
mcp_server get-component dialog --registry shadcn --format json
mcp_server list-components --type ui --platform reactjs --limit 20 --format json
mcp_server set-context reactjs --session-id abc123 --format json
mcp_server list-registries --format json

# RAG Builder CLI (Working) - Pipeline orchestration
rag_builder status --format json
rag_builder list-profiles --format json
rag_builder check --format json

# Content Collection CLI (Working) - Source discovery and content acquisition
content_collection discover --query "react components" --source-type github --limit 10 --format json
content_collection list-source-types --format json
content_collection status --format json

# Extractors CLI (Working) - Content extraction
extractors list-extractors --format json
extractors run-extractor shadcn --format json
extractors run-all-extractors --format json
extractors status --format json

# CLI Tests
python3 v2/core/00-rag-registry/tests/run.py --verbose
python3 v2/core/01-mcp-server/tests/run.py --verbose
python3 v2/03-content-collection/tests/run.py --verbose
python3 v2/04-extractors/tests/run.py --verbose
test_executor v2/core/00-rag-registry/tests/cmd_tests.json
test_executor v2/core/01-mcp-server/tests/mcp_tests.json
test_executor v2/03-content-collection/tests/content_collection_tests.json
test_executor v2/04-extractors/tests/extractor_tests.json
```
