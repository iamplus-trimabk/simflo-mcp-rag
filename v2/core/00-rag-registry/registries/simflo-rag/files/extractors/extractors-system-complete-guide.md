# Extractors System - Complete Guide

## Purpose
Content extraction system that processes raw content from various sources into structured RAG database entries. Supports 11 specialized extractors for different content types and source formats.

## Position in v2 Architecture
This is component **04** in the v2 numbered system:
- **00-rag-registry**: Registry-based RAG database management
- **01-mcp-server**: AI assistant integration via CLI
- **02-rag-builder**: Pipeline orchestration and RAG construction
- **03-content-collection**: Source discovery and content acquisition
- **04-extractors**: Content extraction from various sources (✅ Complete)

## Architecture Overview

### Design Philosophy
SimFlo RAG v2 takes an opinionated approach to content extraction:

**Supported Libraries Only**:
- **shadcn**: Modern React component library with Radix UI primitives
- **gluestack**: Cross-platform component library (React + React Native)

**Key Features**:
- **GitHub CLI Integration**: Uses `gh` command for reliable repository access
- **Local-First**: Repositories downloaded to `$CONTENT_ROOT/github/{repo-name}`
- **No Sample Data**: Only real component data from actual repositories
- **Environment Variables**: Uses `$CONTENT_ROOT` for configurable paths

### Extractor Categories

#### 1. Component Library Extractors
- **shadcn_extractor.py**: Extract shadcn/ui components from registry files
- **gluestack_extractor.py**: Extract gluestack components from monorepo structure

#### 2. Content Type Extractors
- **component_extractor.py**: Generic component extraction from structured sources
- **hooks_extractor.py**: Extract React hooks from source code
- **documentation_extractor.py**: Extract and process documentation content

#### 3. Platform-Specific Extractors
- **react_extractor.py**: React-specific component and pattern extraction
- **react_native_extractor.py**: React Native component extraction
- **vue_extractor.py**: Vue.js component extraction
- **angular_extractor.py**: Angular component extraction

#### 4. Utility Extractors
- **markdown_extractor.py**: Extract content from markdown files
- **json_extractor.py**: Extract structured data from JSON files

## CLI Interface

### Core Commands

#### list - List available extractors
```bash
# List all available extractors
python3 v2/04-extractors/extractors_cli.py list --format json

# List extractors by category
python3 v2/04-extractors/extractors_cli.py list --category component-libraries --format json

# List extractors with table output
python3 v2/04-extractors/extractors_cli.py list --format table
```

**Parameters**:
- `--category`: Filter extractors by category (component-libraries, content-types, platform-specific, utilities)
- `--format`: Output format (json, table)

**Response Example**:
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
        "status": "active"
      },
      {
        "name": "gluestack",
        "description": "Extract gluestack components from monorepo structure",
        "category": "component-libraries",
        "supported_sources": ["github", "local"],
        "status": "active"
      }
    ]
  }
}
```

#### run - Run specific extractor
```bash
# Run shadcn extractor
python3 v2/04-extractors/extractors_cli.py run shadcn --source-type github --output-dir extracted/shadcn/ --format json

# Run gluestack extractor with specific source
python3 v2/04-extractors/extractors_cli.py run gluestack --source-type local --source-path /path/to/gluestack --output-dir extracted/gluestack/ --format json

# Run extractor with specific repository
python3 v2/04-extractors/extractors_cli.py run shadcn --source-type github --repository shadcn-ui/ui --output-dir extracted/shadcn/ --format json
```

**Parameters**:
- `extractor_name`: Name of the extractor to run (required)
- `--source-type`: Type of source (github, local, api)
- `--source-path`: Path to local source (for local source type)
- `--repository`: GitHub repository (format: owner/repo)
- `--output-dir`: Directory to store extracted content (required)
- `--format`: Output format (json, table)

**Response Example**:
```json
{
  "success": true,
  "timestamp": "2025-09-30T21:37:01.043963",
  "data": {
    "extractor": "shadcn",
    "source_type": "github",
    "repository": "shadcn-ui/ui",
    "output_directory": "extracted/shadcn/",
    "components_extracted": 25,
    "hooks_extracted": 8,
    "blocks_extracted": 5,
    "extraction_time": "12.5 seconds",
    "output_files": [
      "extracted/shadcn/components.json",
      "extracted/shadcn/hooks.json",
      "extracted/shadcn/blocks.json"
    ]
  }
}
```

#### run-all - Run all active extractors
```bash
# Run all extractors with default settings
python3 v2/04-extractors/extractors_cli.py run-all --output-dir extracted/all/ --format json

# Run all extractors for specific category
python3 v2/04-extractors/extractors_cli.py run-all --category component-libraries --output-dir extracted/components/ --format json

# Run all extractors with parallel processing
python3 v2/04-extractors/extractors_cli.py run-all --parallel --output-dir extracted/all/ --format json
```

**Parameters**:
- `--category`: Run extractors from specific category only
- `--parallel`: Run extractors in parallel (default: sequential)
- `--output-dir`: Base directory for extracted content
- `--format`: Output format (json, table)

**Response Example**:
```json
{
  "success": true,
  "timestamp": "2025-09-30T21:37:01.043963",
  "data": {
    "total_extractors_run": 11,
    "successful_extractions": 11,
    "failed_extractions": 0,
    "total_output_directory": "extracted/all/",
    "summary": {
      "shadcn": {
        "status": "success",
        "components_extracted": 25,
        "hooks_extracted": 8,
        "output_files": ["extracted/all/shadcn/components.json"]
      },
      "gluestack": {
        "status": "success",
        "components_extracted": 30,
        "hooks_extracted": 12,
        "output_files": ["extracted/all/gluestack/components.json"]
      }
    },
    "total_extraction_time": "45.2 seconds"
  }
}
```

#### status - Get extractor system status
```bash
# Get overall system status
python3 v2/04-extractors/extractors_cli.py status --format json

# Get detailed status with configuration
python3 v2/04-extractors/extractors_cli.py status --detailed --format json

# Get status for specific extractor
python3 v2/04-extractors/extractors_cli.py status --extractor shadcn --format json
```

**Response Example**:
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
    "content_root": "/content",
    "github_cli_available": true,
    "extractors": {
      "shadcn": {
        "status": "active",
        "last_run": "2025-09-30T20:00:00Z",
        "total_extractions": 156,
        "success_rate": 0.98
      },
      "gluestack": {
        "status": "active",
        "last_run": "2025-09-30T19:30:00Z",
        "total_extractions": 89,
        "success_rate": 0.97
      }
    }
  }
}
```

### Configuration Commands

#### config-show - Show extractor configuration
```bash
# Show configuration for all extractors
python3 v2/04-extractors/extractors_cli.py config-show --format json

# Show configuration for specific extractor
python3 v2/04-extractors/extractors_cli.py config-show --extractor shadcn --format json
```

#### config-set - Set extractor configuration
```bash
# Set configuration value
python3 v2/04-extractors/extractors_cli.py config-set --extractor shadcn --key "github_token" --value "ghp_xxxx" --format json

# Set multiple configuration values
python3 v2/04-extractors/extractors_cli.py config-set --extractor gluestack --key "content_root" --value "/new/content/path" --format json
```

## Extractor Details

### shadcn_extractor.py

**Purpose**: Extract shadcn/ui components from registry files using GitHub CLI

**Key Features**:
- **Registry File Parsing**: Parse `apps/www/registry/registry-ui.ts` files
- **Component Metadata**: Extract component descriptions, dependencies, and usage
- **Hook Extraction**: Extract custom React hooks from source code
- **Block Components**: Extract pre-built UI sections and layouts

**Source Requirements**:
- **Repository**: `shadcn-ui/ui`
- **Registry File**: `apps/www/registry/registry-ui.ts`
- **Component Files**: Individual component `.tsx` files
- **Dependencies**: React, Radix UI, Tailwind CSS

**Output Structure**:
```json
{
  "components": [
    {
      "name": "button",
      "description": "Accessible button component with variants",
      "dependencies": ["@radix-ui/react-slot"],
      "install_command": "npx shadcn-ui@latest add button",
      "usage_examples": ["import { Button } from '@/components/ui/button'"],
      "source_file": "apps/www/registry/ui/button.tsx"
    }
  ],
  "hooks": [
    {
      "name": "use-toast",
      "description": "Hook to manage toast notifications",
      "dependencies": ["react"],
      "usage_examples": ["const { toast } = useToast()"],
      "source_file": "apps/www/registry/ui/use-toast.ts"
    }
  ],
  "blocks": [
    {
      "name": "sidebar",
      "description": "Responsive sidebar layout component",
      "components_used": ["button", "sheet", "scroll-area"],
      "usage_examples": ["<Sidebar />"],
      "source_file": "apps/www/registry/ui/sidebar.tsx"
    }
  ]
}
```

### gluestack_extractor.py

**Purpose**: Extract gluestack components from monorepo structure using GitHub CLI

**Key Features**:
- **Monorepo Navigation**: Navigate complex package structures
- **Cross-Platform Support**: Extract both React and React Native components
- **Component Metadata**: Extract component descriptions and platform support
- **Theme Integration**: Extract theme and styling information

**Source Requirements**:
- **Repository**: `gluestack/gluestack-ui-`
- **Package Structure**: `packages/gluestack-core/src/`
- **Component Files**: Platform-specific component implementations
- **Dependencies**: React, React Native, CSS-in-JS libraries

**Output Structure**:
```json
{
  "components": [
    {
      "name": "Button",
      "description": "Cross-platform button component",
      "platforms": ["reactjs", "react-native"],
      "dependencies": ["@gluestack-ui/button"],
      "variants": ["solid", "outline", "ghost"],
      "source_files": {
        "reactjs": "packages/gluestack-core/src/button/Button.tsx",
        "react-native": "packages/gluestack-core/src/button/ButtonNative.tsx"
      }
    }
  ],
  "hooks": [
    {
      "name": "useTheme",
      "description": "Hook for accessing theme configuration",
      "platforms": ["reactjs", "react-native"],
      "dependencies": ["@gluestack-ui/theme"],
      "usage_examples": ["const theme = useTheme()"]
    }
  ]
}
```

## Integration with Content Collection

### Content Flow
1. **Source Discovery**: Content collection discovers repositories and sources
2. **Content Fetching**: Downloads repositories to `$CONTENT_ROOT/github/`
3. **Extraction Processing**: Extractors process downloaded content
4. **Registry Population**: Extracted content organized in registry files
5. **Database Creation**: Registry system creates vector databases

### CLI Pipeline Integration
```bash
# Complete content extraction pipeline
content_discover --query "shadcn components" --source-type github --limit 5 | \
content_fetch --sources - --output-dir $CONTENT_ROOT/github/ | \
extractors_run shadcn --source-type local --source-path $CONTENT_ROOT/github/shadcn-ui/ui --output-dir extracted/shadcn/

# Run all extractors for discovered content
content_discover --query "react component libraries" --source-type github --limit 10 | \
extractors_run-all --parallel --output-dir extracted/all/
```

## Output Formats and Standards

### JSON Output Structure
All extractors follow a consistent JSON output structure:
```json
{
  "metadata": {
    "extractor_name": "shadcn",
    "extraction_timestamp": "2025-09-30T21:37:01.043963",
    "source_repository": "shadcn-ui/ui",
    "source_version": "main",
    "total_components": 25,
    "total_hooks": 8,
    "total_blocks": 5
  },
  "components": [...],
  "hooks": [...],
  "blocks": [...]
}
```

### Registry File Format
Extracted content follows registry file standards:
- **components.json**: Component definitions and metadata
- **hooks.json**: Hook definitions and usage patterns
- **blocks.json**: Block components and layout definitions

## Environment Configuration

### Required Environment Variables
- `CONTENT_ROOT`: Root directory for downloaded content (default: `/content`)
- `GITHUB_TOKEN`: GitHub access token for private repositories (optional)
- `EXTRACTOR_CONFIG_DIR`: Directory for extractor configurations (optional)

### GitHub CLI Setup
The extractors use GitHub CLI for reliable repository access:
```bash
# Install GitHub CLI
brew install gh  # macOS
# or
sudo apt install gh  # Linux

# Authenticate with GitHub
gh auth login

# Verify installation
gh --version
```

## Error Handling and Recovery

### Common Error Scenarios
- **Repository Not Found**: Handle invalid or moved repositories
- **Network Issues**: Retry failed downloads with exponential backoff
- **Parse Errors**: Handle malformed registry files or source code
- **Permission Issues**: Handle access denied for private repositories
- **Disk Space**: Handle insufficient storage for large repositories

### Recovery Strategies
- **Automatic Retry**: Retry failed operations with exponential backoff
- **Fallback Sources**: Use alternative sources when primary fails
- **Partial Recovery**: Process successfully extracted components
- **Error Logging**: Comprehensive error logging for debugging
- **Graceful Degradation**: Continue operation with reduced functionality

## Performance and Optimization

### Parallel Processing
- **Multi-threaded Extraction**: Run multiple extractors in parallel
- **Batch Processing**: Process multiple repositories efficiently
- **Memory Management**: Efficient memory usage for large repositories
- **Caching**: Cache extracted content for faster reprocessing

### Optimization Features
- **Incremental Extraction**: Only extract new or changed content
- **Smart Filtering**: Filter out irrelevant files and directories
- **Compression**: Compress output files to save space
- **Deduplication**: Remove duplicate content across sources

## Testing and Validation

### Test Suite
Run comprehensive extractor tests:
```bash
# Run all extractor tests
python3 v2/04-extractors/tests/run.py --verbose

# Run specific extractor tests
python3 v2/04-extractors/tests/test_shadcn_extractor.py --verbose
```

### Test Coverage
- **Unit Tests**: Individual extractor functionality
- **Integration Tests**: End-to-end extraction workflows
- **Mock Tests**: Test with sample repository data
- **Performance Tests**: Validate extraction speed and resource usage

## Best Practices

### Extraction Best Practices
- **Validate Sources**: Ensure repositories are accessible and valid
- **Handle Errors**: Implement robust error handling and recovery
- **Monitor Performance**: Track extraction time and resource usage
- **Clean Up**: Regular cleanup of temporary files and old content

### Integration Best Practices
- **Pipeline Design**: Design efficient extraction pipelines
- **Error Handling**: Handle errors gracefully at each stage
- **Monitoring**: Monitor extraction system health and performance
- **Documentation**: Document extractor configurations and processes

## Future Enhancements

### Planned Features (v4.0+)
- **Advanced Extractors**: Specialized extractors for complex content types
- **AI-Powered Extraction**: Use AI to identify and extract relevant content
- **Real-time Extraction**: Continuous monitoring and extraction of updates
- **Custom Extractors**: Framework for creating custom extractors

### Extension Points
- **Plugin System**: Support for third-party extractors
- **Custom Formats**: Support for additional output formats
- **Advanced Filtering**: More sophisticated content filtering options
- **Integration APIs**: APIs for external tool integration

This extractors system provides a robust, efficient, and comprehensive content extraction framework that forms the backbone of the SimFlo RAG content processing pipeline.