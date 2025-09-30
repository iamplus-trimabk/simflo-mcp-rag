# simflo-rag v2 - Restructured Architecture

## Purpose
This directory contains the holistically restructured architecture for simflo-rag, designed for long-term maintainability and evolutionary development.

## Components
- **core/**: Essential system components (MCP server, RAG engine, registry system)
- **extractors/**: Content extraction and analysis ecosystem
- **content-collection/**: Content discovery and acquisition

## CLI-First Architecture
All component-to-component communication uses CLI interfaces with simple Python CLI calls.

## Implementation Guidelines
- CLI interfaces for all component communication
- Documentation first - every directory has CLAUDE.md
- Clear boundaries between components
- Evolutionary development approach
- JSON output format for all CLI commands

## Completed Components
- **Registry System**: ✅ Complete - CLI wrapper with list, info, search, and status commands
- **MCP Server**: ✅ Complete - CLI-only architecture with 12 commands for AI assistant integration + comprehensive user guide
- **Extractors**: ✅ Complete - CLI wrapper with access to 11 specialized extractors for content extraction + comprehensive user guide
- **RAG Engine**: ⏳ Pending - Not yet migrated (functionality provided by MCP server)

## CLI Examples
```bash
# Registry System CLI (Working)
v2/core/registry-system/registry.py list --format json
v2/core/registry-system/registry.py info --name shadcn_db --format json
v2/core/registry-system/registry.py search --query "button" --limit 5 --format json
v2/core/registry-system/registry.py status --format json

# MCP Server CLI (Working) - AI Assistant Integration
v2/core/mcp-server/mcp_server.py search "button" --limit 10 --format json
v2/core/mcp-server/mcp_server.py get-component dialog --registry shadcn_db --format json
v2/core/mcp-server/mcp_server.py list-components --type ui --platform reactjs --limit 20 --format json
v2/core/mcp-server/mcp_server.py set-context reactjs --session-id abc123 --format json
v2/core/mcp-server/mcp_server.py list-registries --format json

# Extractors CLI (Working)
v2/extractors/extractors_cli.py list-extractors --format json
v2/extractors/extractors_cli.py run-extractor shadcn --format json
v2/extractors/extractors_cli.py run-all-extractors --format json
v2/extractors/extractors_cli.py status --format json

# CLI Tests
v2/core/registry-system/tests/run.py --verbose
v2/core/mcp-server/tests/run.py --verbose
v2/extractors/tests/run.py --verbose
v2/tests/cmd_test_executor.py v2/core/registry-system/tests/cmd_tests.json
v2/tests/cmd_test_executor.py v2/core/mcp-server/tests/mcp_tests.json
v2/tests/cmd_test_executor.py v2/extractors/tests/extractor_tests.json
```
