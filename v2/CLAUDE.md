# simflo-rag v2 - Restructured Architecture

## Purpose
This directory contains the holistically restructured architecture for simflo-rag, designed for long-term maintainability and evolutionary development.

## Role in System
This is the **future architecture** that will replace the current unstructured codebase. It represents a clean, organized foundation for continued evolution.

## What This Directory Contains
- **core/**: Essential system components (MCP server, RAG engine, registry system)
- **extractors/**: Complete ecosystem for content extraction and analysis
- **content-collection/**: Content discovery, acquisition, and processing
- **data-management/**: Data persistence, schemas, and storage solutions
- **testing/**: Comprehensive testing infrastructure
- **configuration/**: Environment-specific configuration management
- **deployment/**: Build, CI/CD, and containerization
- **monitoring/**: System observability and health monitoring
- **documentation/**: Complete documentation system
- **utilities/**: Shared utilities and helper functions
- **research/**: Experimental features and research tools
- **project-management/**: Project organization and templates

## What This Directory Should NOT Contain
- **Legacy code** from the current root structure
- **Mixed concerns** - each directory has clear boundaries
- **Undocumented files** - every directory has its own CLAUDE.md
- **Hardcoded paths** - all paths should be relative and configurable
- **Scattered configuration** - config belongs in configuration/ directory

## CLI Interface
This root directory provides:
- `setup.py`: Initial setup and dependency installation
- `migrate.py`: Migration tools from current structure
- `test.py`: Full system test runner
- `deploy.py`: Deployment orchestration

## Dependencies and Relationships
- **Independent structure** - no dependencies on current root directory
- **Self-contained** - can be developed and tested separately
- **Migration target** - designed to replace current structure when ready
- **CLI-first** - all components communicate via CLI interfaces

## Implementation Guidelines
1. **No code migration** until structure is fully documented
2. **CLI interfaces** required for all component communication
3. **Documentation first** - every directory must have CLAUDE.md
4. **Clear boundaries** - respect the designated purpose of each directory
5. **Evolutionary development** - small batches, iterative improvement