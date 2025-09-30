# CLI Interface Specifications for Component Communication

## Overview

This document defines the CLI interface specifications for all component-to-component communication in the simflo-rag v2 system. All communication MUST use CLI interfaces as specified.

## Core Principles

1. **CLI-First Architecture**: All component communication MUST use CLI interfaces
2. **Simple Python CLI**: Use argparse and sys.argv, avoid complex CLI packages
3. **JSON I/O Standard**: Use JSON format for data exchange between components
4. **Error Handling**: Consistent exit codes and error messages
5. **Version Compatibility**: Version checking between components

## Communication Patterns

### 1. Command Execution Pattern

```bash
# Basic command structure
component/sub-component/command.py [options] --input /path/to/input.json --output /path/to/output.json

# Example
core/rag-engine/builder.py build --config /path/to/config.json --output /path/to/output.json
```

### 2. Data Flow Pattern

```bash
# Chain commands with JSON pipes
component1/command.py --input input.json --output temp1.json
component2/command.py --input temp1.json --output temp2.json
component3/command.py --input temp2.json --output final.json
```

### 3. Status Query Pattern

```bash
# Query component status
component/status.py --format json
```

## Standard CLI Interface

### Input/Output Standards

**Input**:
- JSON files via `--input` or `--config` flags
- Command-line arguments for simple parameters
- Environment variables for configuration

**Output**:
- JSON files via `--output` flag
- Structured output to stdout with `--format json`
- Human-readable output by default

**Exit Codes**:
- 0: Success
- 1: General error
- 2: Configuration error
- 3: Input validation error
- 4: Processing error
- 5: System error

### Common CLI Arguments

```bash
--input FILE           # Input JSON file
--output FILE          # Output JSON file
--config FILE          # Configuration JSON file
--format FORMAT        # Output format (json, yaml, table)
--verbose              # Verbose output
--quiet               # Minimal output
--version             # Show version
--help                # Show help
```

## Component CLI Specifications

### Core MCP Server

```bash
# Server management
core/mcp-server/server.py start --port 8080 --config /path/to/config.json
core/mcp-server/server.py stop --pid-file /path/to/pid.json
core/mcp-server/server.py status --format json
core/mcp-server/server.py restart --config /path/to/config.json

# Context management
core/mcp-server/context.py set --context /path/to/context.json
core/mcp-server/context.py get --key "key" --format json
core/mcp-server/context.py clear --all

# Request handling
core/mcp-server/request.py handle --request /path/to/request.json --output /path/to/response.json
```

### Core RAG Engine

```bash
# Building operations
core/rag-engine/builder.py build --config /path/to/config.json --output /path/to/output.json
core/rag-engine/builder.py validate --index /path/to/index --output /path/to/validation.json

# Search operations
core/rag-engine/search.py query --index rag-index --query "search terms" --output /path/to/results.json
core/rag-engine/search.py similar --document /path/to/document.json --top-k 10 --output /path/to/results.json

# Vector store operations
core/rag-engine/vector-store.py create --name vector-store --dimension 1536 --output /path/to/config.json
core/rag-engine/vector-store.py add --store vector-store --documents /path/to/documents.json --output /path/to/status.json
core/rag-engine/vector-store.py search --store vector-store --query "query" --output /path/to/results.json
```

### Core Registry System

```bash
# Registry management
core/registry-system/registry-manager.py list --format json
core/registry-system/registry-manager.py add --name registry --path /path/to/registry.json
core/registry-system/registry-manager.py remove --name registry
core/registry-system/registry-manager.py validate --name registry --output /path/to/validation.json

# Metadata operations
core/registry-system/metadata.py get --registry registry --key "key" --output /path/to/metadata.json
core/registry-system/metadata.py set --registry registry --key "key" --value /path/to/value.json
core/registry-system/metadata.py search --registry registry --query "query" --output /path/to/results.json
```

### Extractors

#### Code Extractors
```bash
# React extraction
extractors/code-extractors/react-extractors/extract.py --source /path/to/src --output /path/to/output.json
extractors/code-extractors/react-extractors/analyze-hooks.py --file /path/to/file --output /path/to/output.json

# UI library extraction
extractors/code-extractors/ui-library-extractors/extract-shadcn.py --source /path/to/shadcn --output /path/to/output.json
extractors/code-extractors/ui-library-extractors/extract-gluestack.py --source /path/to/gluestack --output /path/to/output.json
```

#### Language Extractors
```bash
# TypeScript analysis
extractors/language-extractors/typescript-extractor/analyze.py --project /path/to/project --output /path/to/output.json
extractors/language-extractors/typescript-extractor/extract-types.py --source /path/to/src --output /path/to/output.json

# Python analysis
extractors/language-extractors/python-extractor/analyze.py --project /path/to/project --output /path/to/output.json
extractors/language-extractors/python-extractor/extract-modules.py --source /path/to/src --output /path/to/output.json
```

#### Claude Code Extractor
```bash
# AI-powered analysis
extractors/claude-code-extractor/code-analysis/analyze.py --source /path/to/code --output /path/to/output.json
extractors/claude-code-extractor/summarization/summarize.py --input /path/to/input --output /path/to/output.json
extractors/claude-code-extractor/evolution-tracking/analyze-changes.py --repo /path/to/repo --output /path/to/output.json
```

### Content Collection

#### Source Discovery
```bash
# Web search discovery
content-collection/source-discovery/web-search-discovery/search.py --query "search terms" --max-results 50 --output /path/to/output.json
content-collection/source-discovery/web-search-discovery/discover.py --topics /path/to/topics.txt --output /path/to/output.json

# Recommendation engine
content-collection/source-discovery/recommendation-engine/recommend.py --context /path/to/context.json --output /path/to/output.json
```

#### Content Fetching
```bash
# HTTP fetching
content-collection/content-fetching/http-fetchers/fetch.py --url https://example.com --output /path/to/output.json
content-collection/content-fetching/batch-fetchers/process.py --sources /path/to/sources.json --workers 5 --output /path/to/output.json

# API fetching
content-collection/content-fetching/api-fetchers/fetch-api.py --endpoint https://api.example.com/data --output /path/to/output.json
content-collection/content-fetchers/api-fetchers/paginate.py --endpoint https://api.example.com/data --max-pages 10 --output /path/to/output.json
```

#### Content Validation
```bash
# Quality checking
content-collection/content-validation/quality-checkers/assess.py --content /path/to/content --output /path/to/output.json
content-collection/content-validation/relevance-validators/validate.py --content /path/to/content --topic "topic" --output /path/to/output.json
```

### Data Management

#### Database Schemas
```bash
# Schema management
data-management/database-schemas/schema-definitions/create.py --name "schema_name" --tables /path/to/tables.json --output /path/to/output.json
data-management/database-schemas/migration-scripts/apply.py --migration /path/to/migration.sql --database /path/to/database --output /path/to/output.json
```

#### Storage Engines
```bash
# PostgreSQL operations
data-management/storage-engines/postgresql-engine/init.py --config /path/to/config.json --output /path/to/output.json
data-management/storage-engines/postgresql-engine/execute.py --query "SELECT * FROM table" --output /path/to/output.json

# Vector database operations
data-management/storage-engines/vector-db-engines/init.py --engine chromadb --config /path/to/config.json --output /path/to/output.json
data-management/storage-engines/vector-db-engines/index.py --data /path/to/data.json --output /path/to/output.json
```

#### Backup Systems
```bash
# Backup operations
data-management/backup-systems/backup-schedulers/schedule.py --database /path/to/database --frequency daily --output /path/to/output.json
data-management/backup-systems/full-backups/create.py --source /path/to/source --destination /path/to/destination --output /path/to/output.json
data-management/backup-systems/recovery-tools/restore.py --backup /path/to/backup --target /path/to/target --output /path/to/output.json
```

### Testing

#### Unit Testing
```bash
# Test execution
testing/unit-tests/run.py --module /path/to/module --output /path/to/output.json
testing/unit-tests/coverage.py --module /path/to/module --output /path/to/output.json
```

#### Integration Testing
```bash
# Integration tests
testing/integration-tests/run.py --components component1,component2 --output /path/to/output.json
testing/integration-tests/test-api.py --endpoint /path/to/endpoint --output /path/to/output.json
```

#### End-to-End Testing
```bash
# E2E tests
testing/e2e-tests/run.py --scenario /path/to/scenario.json --output /path/to/output.json
testing/e2e-tests/test-ui.py --url https://localhost:5173 --output /path/to/output.json
```

### Configuration

#### Environment Configuration
```bash
# Config management
configuration/environment-configs/generate.py --environment production --output /path/to/output.json
configuration/environment-configs/validate.py --config /path/to/config.json --environment production --output /path/to/output.json

# Feature flags
configuration/feature-flags/enable.py --feature "feature_name" --environment production --output /path/to/output.json
configuration/feature-flags/check.py --feature "feature_name" --environment production --output /path/to/output.json
```

### Monitoring

#### Metrics Collection
```bash
# Metrics
monitoring/metrics-collectors/collect.py --component component_name --metrics cpu,memory --output /path/to/output.json
monitoring/metrics-collectors/export.py --format prometheus --output /path/to/output.json
```

#### Health Checking
```bash
# Health checks
monitoring/health-checkers/check.py --component component_name --endpoint /path/to/endpoint --output /path/to/output.json
monitoring/health-checkers/status.py --system all --output /path/to/output.json
```

### Documentation

#### API Documentation
```bash
# API docs
documentation/api-documentation/generate.py --source /path/to/code --output /path/to/output.json
documentation/api-documentation/update.py --endpoint /path/to/endpoint --docs /path/to/docs --output /path/to/output.json
```

#### User Guides
```bash
# User documentation
documentation/user-guides/create.py --topic "topic_name" --output /path/to/output.json
documentation/user-guides/validate.py --guide /path/to/guide.md --output /path/to/output.json
```

## Data Exchange Formats

### Standard JSON Structure

```json
{
  "version": "1.0",
  "timestamp": "2024-01-01T00:00:00Z",
  "component": "component_name",
  "operation": "operation_name",
  "data": {},
  "metadata": {},
  "status": {
    "code": 0,
    "message": "Success"
  }
}
```

### Error Response Format

```json
{
  "version": "1.0",
  "timestamp": "2024-01-01T00:00:00Z",
  "component": "component_name",
  "operation": "operation_name",
  "error": {
    "code": 1,
    "message": "Error description",
    "details": {}
  },
  "status": {
    "code": 1,
    "message": "Error"
  }
}
```

## Version Compatibility

### Version Checking

```bash
# Check component version
component/version.py --output json

# Expected output
{
  "version": "2.0.0",
  "compatible": ["2.0.0", "2.1.0"],
  "dependencies": {
    "core/mcp-server": ">=2.0.0",
    "core/rag-engine": ">=2.0.0"
  }
}
```

## Best Practices

1. **Consistent Error Handling**: All components must return proper error codes and messages
2. **JSON Validation**: Validate all JSON input and output
3. **Atomic Operations**: Design operations to be atomic and rollback on failure
4. **Logging**: Include comprehensive logging for debugging and monitoring
5. **Performance**: Consider performance impact for large datasets
6. **Security**: Validate all inputs and sanitize outputs
7. **Documentation**: Keep CLI help and documentation up to date

## Implementation Guidelines

1. **Use argparse**: Simple Python argparse for CLI interfaces
2. **Avoid Complex Packages**: Don't use complex CLI frameworks
3. **JSON First**: Use JSON for all data exchange
4. **Exit Codes**: Use standard exit codes consistently
5. **Version Information**: Include version information in all components
6. **Help Documentation**: Provide comprehensive help for all commands
7. **Input Validation**: Validate all inputs before processing