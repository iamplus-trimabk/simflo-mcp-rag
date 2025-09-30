# MCP Server CLI

## Purpose
CLI-only implementation of the MCP server functionality, providing direct command-line interface for AI assistants to interact with component registries.

## Architecture
Replaces the TypeScript MCP protocol server with a Python CLI interface that directly calls data-pipeline modules without HTTP overhead.

## Available Commands

### Component Search & Discovery
```bash
# Search components using natural language
search "button" --limit 10 --platform reactjs --format json

# Get detailed component information
get-component button --registry shadcn_db --format json

# List available components
list-components --type ui --platform reactjs --limit 20 --format json
```

### Context Management
```bash
# Set platform context for intelligent recommendations
set-context reactjs --session-id abc123 --format json

# Get current platform context
get-context --session-id abc123 --format json
```

### Registry Management
```bash
# List available registries
list-registries --platform reactjs --format json
```

### Extraction Management (Not Implemented)
```bash
# These commands return "not implemented" messages
run-extraction --registry shadcn --mode test --format json
extraction-status --format json
list-extraction-registries --format json
clear-extraction-data --registry shadcn --format json
search-by-category "form" components --format json
list-registry-sources shadcn --format json
```

## Integration with Data Pipeline

The CLI directly integrates with existing data-pipeline modules:
- **registry_manager**: Component search, registry management
- **context_manager**: Platform context management
- **vector_store**: Vector search functionality

## Output Format

All commands return structured JSON:
```json
{
  "success": true,
  "timestamp": "2025-09-30T21:37:01.043963",
  "data": {
    // Command-specific data
  }
}
```

## Testing

Run comprehensive test suite:
```bash
# Run all MCP server tests
python3 v2/core/mcp-server/tests/run.py --verbose

# Run specific test file
python3 v2/tests/cmd_test_executor.py v2/core/mcp-server/tests/mcp_tests.json
```

## Test Coverage
- **Total tests**: 14 comprehensive test cases
- **Pass rate**: 100%
- **Coverage**: All working CLI commands, error handling, output formats
- **Extensible**: Easy to add new test cases

## AI Assistant Integration Pattern

AI assistants can use this CLI directly:
```bash
# Example AI assistant integration
python3 v2/core/mcp-server/mcp_server.py search "modal dialog with form validation" --platform reactjs --limit 5 --format json
```

Returns structured JSON with component matches, relevance scores, and installation information.

## Documentation

- **User Guide**: `v2/core/mcp-server/user_guide.md` - Comprehensive usage examples and AI integration patterns
- **Test Suite**: `v2/core/mcp-server/tests/mcp_tests.json` - 14 comprehensive test cases

## Key Benefits
- **Simplicity**: No MCP protocol overhead
- **Performance**: Direct module calls
- **Consistency**: Follows v2 CLI-first architecture
- **Reliability**: Comprehensive test coverage
- **Flexibility**: JSON and table output formats