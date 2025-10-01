# Extractors CLI

## Purpose
CLI interface for orchestrating content extraction from various sources. Provides access to 11 specialized extractors for different component libraries and documentation.

## Architecture
CLI wrapper around existing `/extractors/` modules, following v2 CLI-first architecture principles.

## Available Commands

### Extractor Management
```bash
# List all available extractors
list-extractors --format json

# Get system status
status --format json
```

### Extraction Operations
```bash
# Run specific extractor
run-extractor shadcn --format json

# Run all available extractors
run-all-extractors --format json
```

## Available Extractors

The CLI provides access to specialized extractors:

- **shadcn**: Shadcn components extraction
- **shadcn_hooks**: Shadcn hooks extraction
- **shadcn_components**: Shadcn components specific extraction
- **shadcn_blocks**: Shadcn blocks extraction
- **gluestack**: Gluestack components extraction
- **npm_hooks**: NPM hooks extraction
- **community**: Community components extraction
- **documentation**: Documentation extraction

## Integration with Existing System

The CLI directly integrates with existing extractor modules:
- **extractor_factory**: Extractor discovery and management
- **base_extractor**: Common extraction interfaces
- **Specialized extractors**: Domain-specific extraction logic

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

Run test suite:
```bash
# Run all extractor tests
python3 v2/04-extractors/tests/run.py

# Run specific test file
python3 v2/tests/cmd_test_executor.py v2/04-extractors/tests/extractor_tests.json
```

## Test Coverage
- **Total tests**: 8 essential test cases
- **Coverage**: Core CLI commands, error handling, output formats
- **Focus**: Functional validation, not comprehensive coverage

## Documentation

- **User Guide**: `v2/extractors/user_guide.md` - Comprehensive usage examples and integration patterns
- **Test Suite**: `v2/extractors/tests/extractor_tests.json` - 8 essential test cases

## Key Benefits
- **Orchestration**: Unified interface for multiple extractors
- **Consistency**: Follows v2 CLI-first architecture
- **Flexibility**: Can run individual or all extractors
- **Integration**: Uses existing extraction modules without modification
- **Simplicity**: Minimal CLI wrapper around powerful extraction system