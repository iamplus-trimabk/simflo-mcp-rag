# Extractors CLI User Guide

## Quick Start

The Extractors CLI provides a comprehensive command-line interface for orchestrating content extraction from various sources. This guide covers all available commands with practical examples.

### Basic Usage Pattern

```bash
python3 v2/04-extractors/extractors_cli.py <command> [arguments] --format json
```

All commands support `--format json` (default) and `--format table` output formats.

## Command Reference

### Extractor Discovery & Management

#### list-extractors - List available extractors

List all available specialized extractors with their capabilities.

```bash
# List all extractors
python3 v2/04-extractors/extractors_cli.py list-extractors --format json

# List extractors with table output
python3 v2/04-extractors/extractors_cli.py list-extractors --format table
```

**Output Example:**
```json
{
  "success": true,
  "timestamp": "2025-09-30T22:11:39.989615",
  "data": {
    "total_extractors": 10,
    "extractors": {
      "shadcn": {
        "name": "shadcn",
        "source_types": ["github"],
        "type": "builtin",
        "class": "Not yet imported"
      },
      "gluestack": {
        "name": "gluestack",
        "source_types": ["github"],
        "type": "builtin",
        "class": "Not yet imported"
      }
    }
  }
}
```

#### status - Get extractor system status

Check the status of the extractor system and available modules.

```bash
# Get system status
python3 v2/04-extractors/extractors_cli.py status --format json

# Get status with table output
python3 v2/04-extractors/extractors_cli.py status --format table
```

**Output Example:**
```json
{
  "success": true,
  "timestamp": "2025-09-30T22:11:42.123456",
  "data": {
    "extractors_available": 10,
    "extractor_modules_found": 8,
    "extractors_directory": "/Users/tbardale/v2/simflo-mcp-rag/extractors",
    "directory_exists": true,
    "extractors": ["shadcn", "gluestack", "community", "documentation"]
  }
}
```

### Extraction Operations

#### run-extractor - Run specific extractor

Execute a single extractor for content extraction.

```bash
# Run shadcn extractor
python3 v2/04-extractors/extractors_cli.py run-extractor shadcn --format json

# Run gluestack extractor with table output
python3 v2/04-extractors/extractors_cli.py run-extractor gluestack --format table

# Run community extractor
python3 v2/04-extractors/extractors_cli.py run-extractor community --format json
```

**Output Example:**
```json
{
  "success": true,
  "timestamp": "2025-09-30T22:11:50.217746",
  "data": {
    "extractor": "shadcn",
    "status": "completed",
    "message": "Extractor shadcn executed successfully"
  }
}
```

#### run-all-extractors - Run all available extractors

Execute all available extractors in sequence.

```bash
# Run all extractors
python3 v2/04-extractors/extractors_cli.py run-all-extractors --format json

# Run all extractors with table output
python3 v2/04-extractors/extractors_cli.py run-all-extractors --format table
```

**Output Example:**
```json
{
  "success": true,
  "timestamp": "2025-09-30T22:11:55.987654",
  "data": {
    "total_extractors": 10,
    "results": [
      {
        "extractor": "shadcn",
        "status": "completed",
        "message": "Extractor shadcn executed successfully"
      },
      {
        "extractor": "gluestack",
        "status": "completed",
        "message": "Extractor gluestack executed successfully"
      }
    ],
    "summary": {
      "completed": 8,
      "failed": 2
    }
  }
}
```

## Available Extractors

The CLI provides access to specialized extractors for different content sources:

### Component Library Extractors

- **shadcn**: Shadcn components extraction from GitHub repositories
- **shadcn_components**: Specific Shadcn component extraction
- **shadcn_hooks**: Shadcn hooks extraction
- **shadcn_blocks**: Shadcn block components extraction
- **gluestack**: Gluestack components extraction
- **gluestack_hooks**: Gluestack hooks extraction
- **gluestack_blocks**: Gluestack block components extraction

### General Content Extractors

- **npm_hooks**: NPM package hooks extraction
- **community**: Community components and examples from various sources
- **documentation**: Documentation extraction from web and doc sources

### Extractor Capabilities

Each extractor supports different source types:

- **GitHub**: Extract from GitHub repositories
- **NPM**: Extract from NPM packages
- **Web**: Extract from web pages and documentation sites
- **API**: Extract from REST APIs
- **Local**: Extract from local file systems

## Integration Patterns

### Basic Workflow Example

```bash
# 1. Check system status
python3 v2/04-extractors/extractors_cli.py status --format json

# 2. List available extractors
python3 v2/04-extractors/extractors_cli.py list-extractors --format json

# 3. Run specific extractor
python3 v2/04-extractors/extractors_cli.py run-extractor shadcn --format json

# 4. Run all extractors for comprehensive extraction
python3 v2/04-extractors/extractors_cli.py run-all-extractors --format json
```

### Integration with RAG Pipeline

```bash
# Example: Extract content and then search with MCP server
python3 v2/04-extractors/extractors_cli.py run-extractor shadcn --format json
python3 v2/core/01-mcp-server/mcp_server.py search "button component" --format json
```

### Automation Script Example

```bash
#!/bin/bash
# extract_content.sh - Automated content extraction

echo "Starting content extraction..."
echo "System Status:"
python3 v2/04-extractors/extractors_cli.py status --format table

echo -e "\nRunning all extractors..."
python3 v2/04-extractors/extractors_cli.py run-all-extractors --format json

echo -e "\nExtraction complete!"
```

## Output Format Reference

### Success Response Structure

```json
{
  "success": true,
  "timestamp": "2025-09-30T22:11:39.989615",
  "data": {
    // Command-specific data
  }
}
```

### Error Response Structure

```json
{
  "success": false,
  "timestamp": "2025-09-30T22:11:39.989615",
  "data": {
    "error": "Error message describing what went wrong"
  }
}
```

### Extractor Status Object Structure

```json
{
  "extractor": "extractor_name",
  "status": "completed|failed|initialized",
  "message": "Status message",
  "error": "Error details (if failed)"
}
```

## Common Use Cases

### 1. Component Library Updates

```bash
# Update specific component library
python3 v2/04-extractors/extractors_cli.py run-extractor shadcn --format json
python3 v2/04-extractors/extractors_cli.py run-extractor gluestack --format json
```

### 2. Comprehensive Content Refresh

```bash
# Run all extractors to update entire content database
python3 v2/04-extractors/extractors_cli.py run-all-extractors --format json
```

### 3. System Health Check

```bash
# Check extractor system status
python3 v2/04-extractors/extractors_cli.py status --format json
python3 v2/04-extractors/extractors_cli.py list-extractors --format json
```

### 4. Targeted Extraction

```bash
# Extract from specific source types
python3 v2/04-extractors/extractors_cli.py run-extractor community --format json
python3 v2/04-extractors/extractors_cli.py run-extractor documentation --format json
```

## Troubleshooting

### Common Issues

1. **Extractor not found**
   - Check available extractors: `python3 v2/04-extractors/extractors_cli.py list-extractors --format json`
   - Verify extractor name spelling matches available list

2. **Module import errors**
   - Check system status: `python3 v2/04-extractors/extractors_cli.py status --format json`
   - Verify extractors directory exists and contains modules

3. **Extraction failures**
   - Check individual extractor status in run-all-extractors output
   - Verify extractor has proper configuration if required

4. **Permission issues**
   - Ensure proper file permissions for extractors directory
   - Check network connectivity for GitHub/NPM extractors

### Debug Commands

```bash
# Check system health
python3 v2/04-extractors/extractors_cli.py status --format table

# List available extractors
python3 v2/04-extractors/extractors_cli.py list-extractors --format table

# Test specific extractor
python3 v2/04-extractors/extractors_cli.py run-extractor shadcn --format table
```

### Error Recovery

```bash
# Re-run failed extractors
python3 v2/04-extractors/extractors_cli.py run-extractor <failed_extractor> --format json

# Check what extractors are available vs what failed
python3 v2/04-extractors/extractors_cli.py list-extractors --format json
```

## Advanced Usage

### Table Output for Human Reading

```bash
# Use table format for easier reading
python3 v2/04-extractors/extractors_cli.py status --format table
python3 v2/04-extractors/extractors_cli.py list-extractors --format table
```

### JSON Output for Scripting

```bash
# Use JSON format for automation scripts
python3 v2/04-extractors/extractors_cli.py run-all-extractors --format json | jq '.data.summary.completed'
```

### Combining with Other v2 Components

```bash
# Extract content then search
python3 v2/04-extractors/extractors_cli.py run-extractor shadcn --format json
python3 v2/core/01-mcp-server/mcp_server.py search "shadcn button" --format json

# Check registry content
python3 v2/core/00-rag-registry/registry.py status --format json
```

## Getting Help

- **Command help**: Use `--help` with any command
- **Available extractors**: `python3 v2/04-extractors/extractors_cli.py list-extractors --format json`
- **System status**: `python3 v2/04-extractors/extractors_cli.py status --format json`
- **Test functionality**: `python3 v2/04-extractors/tests/run.py`