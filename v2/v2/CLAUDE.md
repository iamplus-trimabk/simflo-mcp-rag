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
- No code migration until structure is finalized
- CLI interfaces for all component communication
- Documentation first - every directory has CLAUDE.md
- Clear boundaries between components
- Evolutionary development approach
