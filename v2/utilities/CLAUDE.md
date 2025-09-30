# Utilities and Helpers

## Purpose
Shared utilities and helper functions for common operations across all system components.

## Role in System
The **common functionality engine** that provides reusable utilities, helpers, and common functions used throughout the simflo-rag system.

## What This Directory Contains
- **common-functions/**: Common utility functions and helpers
- **formatters/**: Data formatting and conversion utilities
- **validators/**: General validation and checking utilities
- **file-helpers/**: File system and I/O helper functions
- **network-helpers/**: Network and HTTP helper utilities
- **crypto-helpers/**: Cryptography and security helper functions
- **logging-helpers/**: Logging and debugging utilities
- **config-helpers/**: Configuration parsing and management helpers

## What This Directory Should NOT Contain
- **Business logic** - belongs in core/ or specific functional areas
- **Component-specific code** - belongs in respective components
- **Configuration files** - belongs in configuration/
- **Test code** - belongs in testing/

## CLI Interface
```bash
# Common functions
utilities/common-functions/list.py --category category_name --output /path/to/output
utilities/common-functions/test.py --function function_name --output /path/to/output
utilities/common-functions/document.py --function function_name --output /path/to/output

# Formatters
utilities/formatters/format.py --input /path/to/input --format json --output /path/to/output
utilities/formatters/convert.py --input /path/to/input --from-format csv --to-format json --output /path/to/output
utilities/formatters/validate.py --input /path/to/input --format json --output /path/to/output

# Validators
utilities/validators/validate.py --input /path/to/input --type email --output /path/to/output
utilities/validators/check.py --input /path/to/input --rules /path/to/rules.json --output /path/to/output
utilities/validators/sanitize.py --input /path/to/input --output /path/to/output

# File helpers
utilities/file-helpers/read.py --file /path/to/file --output /path/to/output
utilities/file-helpers/write.py --content "content" --file /path/to/file --output /path/to/output
utilities/file-helpers/list.py --directory /path/to/directory --pattern "*.py" --output /path/to/output

# Network helpers
utilities/network-helpers/fetch.py --url https://example.com --output /path/to/output
utilities/network-helpers/request.py --method GET --url https://example.com --output /path/to/output
utilities/network-helpers/test.py --endpoint https://api.example.com --output /path/to/output

# Crypto helpers
utilities/crypto-helpers/hash.py --input /path/to/input --algorithm sha256 --output /path/to/output
utilities/crypto-helpers/encrypt.py --input /path/to/input --key /path/to/key --output /path/to/output
utilities/crypto-helpers/generate.py --type random --length 32 --output /path/to/output

# Logging helpers
utilities/logging-helpers/setup.py --config /path/to/config.json --output /path/to/output
utilities/logging-helpers/log.py --message "message" --level info --output /path/to/output
utilities/logging-helpers/rotate.py --logs /path/to/logs --output /path/to/output

# Config helpers
utilities/config-helpers/parse.py --config /path/to/config.json --output /path/to/output
utilities/config-helpers/validate.py --config /path/to/config.json --schema /path/to/schema.json --output /path/to/output
utilities/config-helpers/merge.py --config1 /path/to/config1.json --config2 /path/to/config2.json --output /path/to/output
```

## Dependencies and Relationships
- **Uses**: Minimal external dependencies, focuses on core utilities
- **Provides**: Common functionality to all system components
- **Integrates with:** All system components that need utility functions
- **Serves**: Cross-cutting concerns and common functionality needs

## Implementation Guidelines
1. **Reusability** - create functions that can be reused across multiple components
2. **Simplicity** - keep utility functions simple and focused
3. **Documentation** - provide clear documentation and examples
4. **Testing** - thoroughly test utility functions as they're used widely
5. **Performance** - optimize utility functions for performance as they're used frequently