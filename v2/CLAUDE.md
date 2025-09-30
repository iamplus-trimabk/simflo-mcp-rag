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
- **MCP Server**: ⏳ Pending - Not yet migrated
- **RAG Engine**: ⏳ Pending - Not yet migrated

## CLI Examples
```bash
# Registry System CLI (Working)
v2/core/registry-system/registry.py list --format json
v2/core/registry-system/registry.py info --name shadcn_db --format json
v2/core/registry-system/registry.py search --query "button" --limit 5 --format json
v2/core/registry-system/registry.py status --format json
```
