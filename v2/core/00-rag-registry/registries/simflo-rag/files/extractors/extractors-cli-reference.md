# Extractors CLI Reference

## Quick Start

The Extractors CLI provides a comprehensive command-line interface for extracting structured content from various sources into RAG database entries. This reference covers all available commands with practical examples.

### Basic Usage Pattern

```bash
python3 v2/04-extractors/extractors_cli.py <command> [arguments] --format json
```

All commands support `--format json` (default) and `--format table` output formats.

## Command Reference

### Extractor Management

#### list - List available extractors

List all available extractors with optional category filtering.

```bash
# List all extractors
python3 v2/04-extractors/extractors_cli.py list

# List extractors by category
python3 v2/04-extractors/extractors_cli.py list --category component-libraries

# List extractors with table output
python3 v2/04-extractors/extractors_cli.py list --format table
```

**Parameters**:
- `--category`: Filter by category (component-libraries, content-types, platform-specific, utilities)
- `--format`: Output format (json, table)

**Output Example**:
```json
{
  "success": true,
  "timestamp": "2025-09-30T21:37:01.043963",
  "data": {
    "total_extractors": 11,
    "extractors": [
      {
        "name": "shadcn",
        "description": "Extract shadcn/ui components from registry files",
        "category": "component-libraries",
        "supported_sources": ["github", "local"],
        "status": "active",
        "last_run": "2025-09-30T20:00:00Z"
      },
      {
        "name": "gluestack",
        "description": "Extract gluestack components from monorepo structure",
        "category": "component-libraries",
        "supported_sources": ["github", "local"],
        "status": "active",
        "last_run": "2025-09-30T19:30:00Z"
      }
    ]
  }
}
```

#### run - Run specific extractor

Execute a specific extractor to process content from a source.

```bash
# Run shadcn extractor with GitHub source
python3 v2/04-extractors/extractors_cli.py run shadcn --source-type github --repository shadcn-ui/ui --output-dir extracted/shadcn/

# Run gluestack extractor with local source
python3 v2/04-extractors/extractors_cli.py run gluestack --source-type local --source-path /path/to/gluestack --output-dir extracted/gluestack/

# Run extractor with custom repository
python3 v2/04-extractors/extractors_cli.py run shadcn --source-type github --repository my-org/shadcn-custom --output-dir extracted/custom/
```

**Parameters**:
- `extractor_name`: Name of the extractor to run (required)
- `--source-type`: Type of source (github, local, api)
- `--repository`: GitHub repository (format: owner/repo) - for github source type
- `--source-path`: Path to local source - for local source type
- `--output-dir`: Directory to store extracted content (required)
- `--format`: Output format (json, table)

**Output Example**:
```json
{
  "success": true,
  "timestamp": "2025-09-30T21:37:01.043963",
  "data": {
    "extractor": "shadcn",
    "source_type": "github",
    "repository": "shadcn-ui/ui",
    "output_directory": "extracted/shadcn/",
    "extraction_summary": {
      "components_extracted": 25,
      "hooks_extracted": 8,
      "blocks_extracted": 5,
      "total_files_processed": 156
    },
    "output_files": [
      "extracted/shadcn/components.json",
      "extracted/shadcn/hooks.json",
      "extracted/shadcn/blocks.json"
    ],
    "extraction_time": "12.5 seconds"
  }
}
```

#### run-all - Run all active extractors

Execute all active extractors or extractors from a specific category.

```bash
# Run all extractors with default settings
python3 v2/04-extractors/extractors_cli.py run-all --output-dir extracted/all/

# Run extractors from specific category
python3 v2/04-extractors/extractors_cli.py run-all --category component-libraries --output-dir extracted/components/

# Run all extractors in parallel
python3 v2/04-extractors/extractors_cli.py run-all --parallel --output-dir extracted/all/
```

**Parameters**:
- `--category`: Run extractors from specific category only
- `--parallel`: Run extractors in parallel (default: sequential)
- `--output-dir`: Base directory for extracted content
- `--format`: Output format (json, table)

**Output Example**:
```json
{
  "success": true,
  "timestamp": "2025-09-30T21:37:01.043963",
  "data": {
    "total_extractors_run": 11,
    "successful_extractions": 11,
    "failed_extractions": 0,
    "parallel_execution": true,
    "total_output_directory": "extracted/all/",
    "total_extraction_time": "45.2 seconds",
    "extraction_summary": {
      "shadcn": {
        "status": "success",
        "components_extracted": 25,
        "hooks_extracted": 8,
        "blocks_extracted": 5
      },
      "gluestack": {
        "status": "success",
        "components_extracted": 30,
        "hooks_extracted": 12,
        "blocks_extracted": 8
      }
    }
  }
}
```

### System Status

#### status - Get extractor system status

Get comprehensive status information about the extractor system.

```bash
# Get overall system status
python3 v2/04-extractors/extractors_cli.py status

# Get detailed status with configuration
python3 v2/04-extractors/extractors_cli.py status --detailed

# Get status for specific extractor
python3 v2/04-extractors/extractors_cli.py status --extractor shadcn

# Get status with table output
python3 v2/04-extractors/extractors_cli.py status --format table
```

**Parameters**:
- `--detailed`: Include detailed configuration information
- `--extractor`: Show status for specific extractor only
- `--format`: Output format (json, table)

**Output Example**:
```json
{
  "success": true,
  "timestamp": "2025-09-30T21:37:01.043963",
  "data": {
    "system_status": "operational",
    "total_extractors": 11,
    "active_extractors": 11,
    "supported_source_types": ["github", "local", "api"],
    "last_extraction": "2025-09-30T20:00:00Z",
    "environment": {
      "content_root": "/content",
      "github_cli_available": true,
      "github_authenticated": true
    },
    "extractors": {
      "shadcn": {
        "status": "active",
        "last_run": "2025-09-30T20:00:00Z",
        "total_extractions": 156,
        "success_rate": 0.98,
        "average_extraction_time": "12.3s"
      },
      "gluestack": {
        "status": "active",
        "last_run": "2025-09-30T19:30:00Z",
        "total_extractions": 89,
        "success_rate": 0.97,
        "average_extraction_time": "15.7s"
      }
    }
  }
}
```

### Configuration Management

#### config-show - Show extractor configuration

Display current configuration for extractors.

```bash
# Show configuration for all extractors
python3 v2/04-extractors/extractors_cli.py config-show

# Show configuration for specific extractor
python3 v2/04-extractors/extractors_cli.py config-show --extractor shadcn

# Show configuration with table output
python3 v2/04-extractors/extractors_cli.py config-show --format table
```

**Parameters**:
- `--extractor`: Show configuration for specific extractor only
- `--format`: Output format (json, table)

**Output Example**:
```json
{
  "success": true,
  "timestamp": "2025-09-30T21:37:01.043963",
  "data": {
    "global_config": {
      "content_root": "/content",
      "parallel_processing": true,
      "max_workers": 4
    },
    "extractor_configs": {
      "shadcn": {
        "registry_file_path": "apps/www/registry/registry-ui.ts",
        "component_file_pattern": "apps/www/registry/ui/*.tsx",
        "hook_file_pattern": "apps/www/registry/ui/*.ts",
        "supported_variants": ["default", "destructive", "outline", "secondary", "ghost", "link"]
      },
      "gluestack": {
        "component_base_path": "packages/gluestack-core/src",
        "platform_patterns": {
          "reactjs": "*.tsx",
          "react-native": "*.native.tsx"
        }
      }
    }
  }
}
```

#### config-set - Set extractor configuration

Update configuration values for extractors.

```bash
# Set global configuration
python3 v2/04-extractors/extractors_cli.py config-set --key "content_root" --value "/new/content/path"

# Set extractor-specific configuration
python3 v2/04-extractors/extractors_cli.py config-set --extractor shadcn --key "github_token" --value "ghp_xxxx"

# Set boolean configuration
python3 v2/04-extractors/extractors_cli.py config-set --extractor gluestack --key "parallel_processing" --value "true"

# Set array configuration
python3 v2/04-extractors/extractors_cli.py config-set --extractor shadcn --key "supported_variants" --value '["default","destructive","outline"]'
```

**Parameters**:
- `--extractor`: Target extractor name (optional for global config)
- `--key`: Configuration key (required)
- `--value`: Configuration value (required)

**Output Example**:
```json
{
  "success": true,
  "timestamp": "2025-09-30T21:37:01.043963",
  "data": {
    "message": "Configuration updated successfully",
    "extractor": "shadcn",
    "key": "github_token",
    "old_value": null,
    "new_value": "ghp_xxxx",
    "config_file": "/path/to/config/shadcn.json"
  }
}
```

## Extractor Categories

### Component Libraries

#### shadcn
Extract shadcn/ui components from registry files.

**Features**:
- Registry file parsing (`apps/www/registry/registry-ui.ts`)
- Component metadata extraction
- Hook extraction from source code
- Block component extraction

**Usage Examples**:
```bash
# Extract from main shadcn repository
python3 v2/04-extractors/extractors_cli.py run shadcn --source-type github --repository shadcn-ui/ui --output-dir extracted/shadcn/

# Extract from local shadcn fork
python3 v2/04-extractors/extractors_cli.py run shadcn --source-type local --source-path ~/projects/shadcn-fork --output-dir extracted/shadcn-local/
```

#### gluestack
Extract gluestack components from monorepo structure.

**Features**:
- Monorepo navigation (`packages/gluestack-core/src/`)
- Cross-platform component extraction (React + React Native)
- Theme integration extraction
- Variant and prop extraction

**Usage Examples**:
```bash
# Extract from gluestack repository
python3 v2/04-extractors/extractors_cli.py run gluestack --source-type github --repository gluestack/gluestack-ui- --output-dir extracted/gluestack/

# Extract with specific platform focus
python3 v2/04-extractors/extractors_cli.py run gluestack --source-type github --repository gluestack/gluestack-ui-react --output-dir extracted/gluestack-react/
```

### Content Types

#### component_extractor
Generic component extraction from structured sources.

**Features**:
- Framework-agnostic component parsing
- Dependency extraction
- Usage pattern analysis
- Prop and slot identification

#### hooks_extractor
Extract React hooks from source code.

**Features**:
- Hook pattern recognition (`use-*`)
- Custom hook identification
- Dependency tracking
- Return type analysis

#### documentation_extractor
Extract and process documentation content.

**Features**:
- Markdown parsing
- API documentation extraction
- Tutorial and guide processing
- Code example extraction

### Platform-Specific

#### react_extractor
React-specific component and pattern extraction.

#### react_native_extractor
React Native component extraction.

#### vue_extractor
Vue.js component extraction.

#### angular_extractor
Angular component extraction.

### Utilities

#### markdown_extractor
Extract content from markdown files.

#### json_extractor
Extract structured data from JSON files.

## Output Formats

### JSON Format (Default)
Structured JSON output for programmatic consumption:

```json
{
  "success": true,
  "timestamp": "2025-09-30T21:37:01.043963",
  "data": {
    // Command-specific data
  }
}
```

### Table Format
Human-readable table format for console output:

```
| Extractor | Category      | Status | Last Run      | Success Rate |
|-----------|---------------|--------|---------------|--------------|
| shadcn    | component-libraries | active | 2025-09-30T20:00:00Z | 98% |
| gluestack | component-libraries | active | 2025-09-30T19:30:00Z | 97% |
```

## Integration Patterns

### Basic Extraction Workflow

```bash
# 1. Check system status
python3 v2/04-extractors/extractors_cli.py status

# 2. List available extractors
python3 v2/04-extractors/extractors_cli.py list --category component-libraries

# 3. Run specific extractor
python3 v2/04-extractors/extractors_cli.py run shadcn --source-type github --repository shadcn-ui/ui --output-dir extracted/shadcn/

# 4. Verify extraction results
python3 v2/04-extractors/extractors_cli.py status --extractor shadcn
```

### Batch Processing Workflow

```bash
# 1. Run all component library extractors
python3 v2/04-extractors/extractors_cli.py run-all --category component-libraries --parallel --output-dir extracted/components/

# 2. Run all extractors
python3 v2/04-extractors/extractors_cli.py run-all --parallel --output-dir extracted/all/

# 3. Check overall system status
python3 v2/04-extractors/extractors_cli.py status --detailed
```

### Pipeline Integration

```bash
# Content collection to extraction pipeline
content_discover --query "react component libraries" --source-type github --limit 5 | \
content_fetch --sources - --output-dir $CONTENT_ROOT/github/ | \
extractors_run-all --parallel --output-dir extracted/libraries/

# Specific repository extraction
content_discover --query "shadcn" --source-type github --limit 1 | \
extractors_run shadcn --source-type local --source-path $CONTENT_ROOT/github/shadcn-ui/ui --output-dir extracted/shadcn/
```

## Error Handling

### Common Error Responses

```json
{
  "success": false,
  "timestamp": "2025-09-30T21:37:01.043963",
  "error": "Extractor 'unknown' not found",
  "error_code": "EXTRACTOR_NOT_FOUND",
  "suggestions": ["Use 'list' command to see available extractors"]
}
```

### Troubleshooting Commands

```bash
# Check system status
python3 v2/04-extractors/extractors_cli.py status --detailed

# Verify extractor configuration
python3 v2/04-extractors/extractors_cli.py config-show --extractor shadcn

# Test with a small extraction
python3 v2/04-extractors/extractors_cli.py run shadcn --source-type github --repository shadcn-ui/ui --output-dir test-extraction/

# Check GitHub CLI availability
python3 v2/04-extractors/extractors_cli.py status --detailed | grep github_cli
```

## Getting Help

- **Command help**: Use `--help` with any command
- **Available extractors**: `python3 v2/04-extractors/extractors_cli.py list`
- **System status**: `python3 v2/04-extractors/extractors_cli.py status`
- **Configuration**: `python3 v2/04-extractors/extractors_cli.py config-show`

## Performance Tips

1. **Use Parallel Processing**: `--parallel` flag for faster execution
2. **Optimize Content Root**: Set `CONTENT_ROOT` to fast storage
3. **Monitor Resources**: Use `status --detailed` to track performance
4. **Batch Operations**: Use `run-all` instead of multiple individual runs
5. **Regular Cleanup**: Clean old extraction directories to save space