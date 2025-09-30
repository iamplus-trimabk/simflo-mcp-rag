# Core System Components

## Purpose
Contains the essential system components that form the backbone of simflo-rag functionality.

## Components
- **mcp-server/**: MCP protocol server implementation
- **rag-engine/**: RAG construction, search, and management  
- **registry-system/**: Central registry coordination and metadata

## CLI Interface
```bash
core/rag-engine/builder.py build --config config.json
core/registry-system/registry.py list --format json
core/registry-system/registry.py info --name shadcn_db --format json
core/registry-system/registry.py search --query "button" --limit 10 --format json
core/registry-system/registry.py status --format json
core/mcp-server/mcp_server.py search "button" --limit 10 --format json
core/mcp-server/mcp_server.py get-component dialog --registry shadcn_db --format json
core/mcp-server/mcp_server.py list-registries --format json
core/mcp-server/mcp_server.py set-context reactjs --format json
```

## Registry System CLI
The registry system provides a CLI interface for managing and searching multiple RAG databases.

### Commands
- **list**: List all available registries
- **info**: Get information about a specific registry
- **search**: Search across all registries for components
- **status**: Get system status and statistics

### Output Formats
All commands support `--format json` (default) and `--format table` output formats.

### Examples
```bash
# List all registries
python3 core/registry-system/registry.py list --format json

# Get registry information
python3 core/registry-system/registry.py info --name shadcn_db --format json

# Search for components
python3 core/registry-system/registry.py search --query "button" --limit 5 --format json

# Get system status
python3 core/registry-system/registry.py status --format json
```

## Test Infrastructure
The registry system includes comprehensive test infrastructure with JSON-based test definitions.

### Test Components
- **cmd_test_executor.py**: Core test execution engine in `v2/tests/`
- **cmd_tests.json**: 27 comprehensive test definitions
- **run.py**: Test runner script for easy test execution

### Running Tests
```bash
# Run all registry system tests
python3 v2/core/registry-system/tests/run.py

# Run with verbose output
python3 v2/core/registry-system/tests/run.py --verbose

# Generate test report
python3 v2/core/registry-system/tests/run.py --output test_report.json

# Run specific test file
python3 v2/tests/cmd_test_executor.py v2/core/registry-system/tests/cmd_tests.json
```

### Test Coverage
- ✅ **Basic functionality**: List, info, search, status commands
- ✅ **Output formats**: JSON and table formats
- ✅ **Error handling**: Invalid arguments and missing parameters
- ✅ **Help commands**: All help options
- ✅ **Edge cases**: Empty results, working directory changes

### Current Test Status
- **Registry System**: 8 essential test cases (100% pass rate)
- **MCP Server**: 14 comprehensive test cases (100% pass rate)
- **Framework**: Complete and functional
- **Extensible**: Easy to add new test cases

## MCP Server CLI

The MCP server provides a comprehensive CLI interface for AI assistant integration, replacing the TypeScript MCP protocol server with a direct CLI approach.

### Commands
- **search**: Search for components using natural language queries
- **get-component**: Get detailed information about specific components
- **list-components**: List available components with filtering options
- **set-context**: Set platform context for intelligent recommendations
- **get-context**: Get current platform context
- **list-registries**: List available component registries
- **Extraction commands**: run-extraction, extraction-status, list-extraction-registries, clear-extraction-data (not implemented yet)

### AI Assistant Integration
```bash
# Component search and discovery
python3 v2/core/mcp-server/mcp_server.py search "modal dialog" --limit 5 --format json

# Get component details
python3 v2/core/mcp-server/mcp_server.py get-component button --registry shadcn_db --format json

# Set platform context
python3 v2/core/mcp-server/mcp_server.py set-context reactjs --session-id abc123 --format json
```

### Output Format
All commands support `--format json` (default) and `--format table` output formats with structured JSON response containing `success`, `timestamp`, and `data` fields.

### Documentation
- **User Guide**: `v2/core/mcp-server/user_guide.md` - Comprehensive usage examples and AI integration patterns
