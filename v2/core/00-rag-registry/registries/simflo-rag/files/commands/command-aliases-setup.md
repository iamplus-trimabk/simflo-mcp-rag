# Command Aliases Setup Guide

## Purpose
Setup and usage guide for the SimFlo RAG v2 command alias system, which provides convenient shortcuts for all CLI commands across the system components.

## Quick Setup

### Enable Command Aliases
```bash
# Enable aliases for current session
source v2/commands.sh

# Add to shell profile for persistence
echo 'source /path/to/simflo-rag/v2/commands.sh' >> ~/.zshrc
# or for bash
echo 'source /path/to/simflo-rag/v2/commands.sh' >> ~/.bashrc
```

### Verify Setup
```bash
# Test basic functionality
simflo_help
simflo_status
```

## Available Aliases

### Helper Functions

#### simflo_help - Show command reference
```bash
# Show all available commands
simflo_help

# Show specific category
simflo_help registry
simflo_help mcp
simflo_help content
simflo_help extractors
simflo_help rag_builder
```

**Output**:
```
SimFlo RAG v2 Command Reference

=== Registry Commands ===
rag_registry list                    - List all available registries
rag_registry_info --name shadcn     - Get detailed registry information
rag_registry_search --query "button" - Search across all registries
rag_registry_status                  - Get overall system status
rag_registry_clean --registry shadcn - Clean registry database
rag_registry_rebuild --registry shadcn - Rebuild registry database

=== MCP Server Commands ===
mcp_search "button"                  - Search for components
mcp_get_component button             - Get component details
mcp_list_components --type ui        - List available components
mcp_set_context reactjs              - Set platform context
mcp_get_context                      - Get current platform context
mcp_list_registries                  - List available registries
mcp_run_extraction --registry shadcn - Run extraction for registry
mcp_extraction_status                - Get extraction system status
...
```

#### simflo_setup - Test core components functionality
```bash
# Test all core components
simflo_setup

# Test specific component
simflo_setup registry
simflo_setup mcp
simflo_setup content
simflo_setup extractors
simflo_setup rag_builder
```

**Output**:
```
Testing SimFlo RAG v2 Components...

✅ Registry System: OK (3 registries available)
✅ MCP Server: OK (18 commands available)
✅ Content Collection: OK (4 source types supported)
✅ Extractors: OK (11 extractors active)
✅ RAG Builder: OK (3 profiles available)

All components operational!
```

#### simflo_status - Quick status across all components
```bash
# Show status of all components
simflo_status

# Detailed status
simflo_status --detailed
```

**Output**:
```
SimFlo RAG v2 System Status

=== Registry System ===
Status: Operational
Registries: 3 active (shadcn, gluestack, simflo-rag)
Total Documents: 156
Last Updated: 2025-09-30T20:00:00Z

=== MCP Server ===
Status: Operational
Commands Available: 18
Extraction System: Ready
Context Sessions: 2 active

=== Content Collection ===
Status: Operational
Supported Sources: github, npm, docs, community
Total Discovered: 234 sources
Last Collection: 2025-09-30T19:00:00Z

=== Extractors ===
Status: Operational
Active Extractors: 11
Last Extraction: 2025-09-30T18:30:00Z
Success Rate: 98.5%

=== RAG Builder ===
Status: Operational
Available Profiles: 3
Last Build: 2025-09-30T17:00:00Z
```

#### simflo_test - Run core test suites
```bash
# Run all tests
simflo_test

# Run specific tests
simflo_test registry
simflo_test mcp
simflo_test content
simflo_test extractors
simflo_test rag_builder
```

**Output**:
```
Running SimFlo RAG v2 Test Suites...

=== Registry Tests ===
Running 8 essential test cases...
✅ List registries test
✅ Registry info test
✅ Search functionality test
✅ Status command test
✅ Clean database test
✅ Rebuild database test
✅ Error handling test
✅ Output format test
Registry Tests: 8/8 PASSED

=== MCP Server Tests ===
Running 14 comprehensive test cases...
✅ Search command test
✅ Get component test
✅ List components test
✅ Set context test
✅ Get context test
✅ List registries test
✅ Extraction commands test
✅ Error handling test
MCP Server Tests: 14/14 PASSED

All test suites PASSED! (32/32 tests)
```

### Registry Commands (00-rag-registry)

#### rag_registry list - List all available registries
```bash
# Full command equivalent
python3 v2/core/00-rag-registry/registry.py list --format json

# Alias
rag_registry list

# Table output
rag_registry list --format table
```

#### rag_registry_info - Get detailed registry information
```bash
# Full command equivalent
python3 v2/core/00-rag-registry/registry.py info --name shadcn --format json

# Alias
rag_registry_info --name shadcn

# With table output
rag_registry_info --name shadcn --format table
```

#### rag_registry_search - Search across all registries
```bash
# Full command equivalent
python3 v2/core/00-rag-registry/registry.py search --query "button component" --limit 10 --format json

# Alias
rag_registry_search --query "button" --limit 5

# Natural language search
rag_registry_search --query "form input with validation" --limit 10
```

#### rag_registry_status - Get overall system status
```bash
# Full command equivalent
python3 v2/core/00-rag-registry/registry.py status --format json

# Alias
rag_registry_status

# Detailed status
rag_registry_status --detailed
```

#### rag_registry_clean - Clean registry database
```bash
# Full command equivalent
python3 v2/core/00-rag-registry/registry.py clean-db --registry shadcn --format json

# Alias
rag_registry_clean --registry shadcn

# Clean all data
rag_registry_clean_all --registry shadcn
```

#### rag_registry_rebuild - Rebuild registry database
```bash
# Full command equivalent
python3 v2/core/00-rag-registry/registry.py rebuild-db --registry shadcn --format json

# Alias
rag_registry_rebuild --registry shadcn
```

### MCP Server Commands (01-mcp-server)

#### Component Search Commands
```bash
# Search components
mcp_search "button" --limit 10
mcp_search "modal dialog" --platform reactjs --limit 5
mcp_search "form with validation" --limit 15

# Get component details
mcp_get_component button
mcp_get_component dialog --registry shadcn
mcp_get_component input --format table

# List components
mcp_list_components --type ui --platform reactjs --limit 20
mcp_list_components --type hooks --limit 30
mcp_list_components --limit 50
```

#### Context Management Commands
```bash
# Set context
mcp_set_context reactjs --session-id web-dev-001
mcp_set_context reactnative --session-id mobile-dev-002
mcp_set_context documentation --session-id ai-learning

# Get context
mcp_get_context
mcp_get_context --session-id web-dev-001
```

#### Registry Management Commands
```bash
# List registries
mcp_list_registries
mcp_list_registries --platform reactjs
mcp_list_registries --format table
```

#### Extraction Commands
```bash
# Run extraction
mcp_run_extraction --registry shadcn
mcp_run_extraction --registry gluestack --mode production

# Extraction status
mcp_extraction_status

# List extraction registries
mcp_list_extraction_registries

# Clear extraction data
mcp_clear_extraction_data --registry shadcn

# Search by category
mcp_search_by_category "button" components
mcp_search_by_category "form" hooks
mcp_search_by_category "sidebar" blocks

# List registry sources
mcp_list_registry_sources shadcn
```

### Content Collection Commands (03-content-collection)

#### Source Discovery Commands
```bash
# Discover sources
content_discover --query "react components" --source-type github --limit 10
content_discover --query "react hooks" --source-type npm --limit 15
content_discover --query "documentation" --source-type docs --limit 5
content_discover --query "tutorials" --source-type community --limit 8
```

#### Content Fetching Commands
```bash
# Fetch from sources file
content_fetch --sources-file sources.json --output-dir raw_content/

# Fetch from specific source
content_fetch --source "https://github.com/shadcn-ui/ui" --output-dir raw_content/shadcn/

# Fetch with depth control
content_fetch --sources-file sources.json --output-dir raw_content/ --depth 1
```

#### System Status Commands
```bash
# System status
content_status
content_status --detailed

# List source types
content_list_source_types
content_list_source_types --detailed
```

### Extractor Commands (04-extractors)

#### Extractor Management Commands
```bash
# List extractors
extractors_list
extractors_list --category component-libraries
extractors_list --format table
```

#### Extraction Commands
```bash
# Run specific extractor
extractors_run shadcn
extractors_run gluestack
extractors_run shadcn --source-type github --repository my-org/shadcn-custom

# Run all extractors
extractors_run_all
extractors_run_all --category component-libraries
extractors_run_all --parallel
```

#### Status Commands
```bash
# System status
extractors_status
extractors_status --detailed
extractors_status --extractor shadcn
```

### RAG Builder Commands (02-rag-builder)

#### Pipeline Commands
```bash
# Pipeline status
rag_builder_status

# List profiles
rag_builder_list_profiles

# System check
rag_builder_check
```

## Command Aliases Script

### Source: v2/commands.sh
```bash
#!/bin/bash

# SimFlo RAG v2 Command Aliases
# Source this file to enable convenient command aliases

# Helper Functions
alias simflo_help='python3 v2/scripts/help.py'
alias simflo_setup='python3 v2/scripts/setup.py'
alias simflo_status='python3 v2/scripts/status.py'
alias simflo_test='python3 v2/scripts/test.py'

# Registry Commands (00-rag-registry)
alias rag_registry_list='python3 v2/core/00-rag-registry/registry.py list --format json'
alias rag_registry_info='python3 v2/core/00-rag-registry/registry.py info'
alias rag_registry_search='python3 v2/core/00-rag-registry/registry.py search'
alias rag_registry_status='python3 v2/core/00-rag-registry/registry.py status --format json'
alias rag_registry_clean='python3 v2/core/00-rag-registry/registry.py clean-db'
alias rag_registry_clean_all='python3 v2/core/00-rag-registry/registry.py clean-all'
alias rag_registry_rebuild='python3 v2/core/00-rag-registry/registry.py rebuild-db'

# MCP Server Commands (01-mcp-server)
alias mcp_search='python3 v2/core/01-mcp-server/mcp_server.py search'
alias mcp_get_component='python3 v2/core/01-mcp-server/mcp_server.py get-component'
alias mcp_list_components='python3 v2/core/01-mcp-server/mcp_server.py list-components'
alias mcp_set_context='python3 v2/core/01-mcp-server/mcp_server.py set-context'
alias mcp_get_context='python3 v2/core/01-mcp-server/mcp_server.py get-context'
alias mcp_list_registries='python3 v2/core/01-mcp-server/mcp_server.py list-registries'
alias mcp_run_extraction='python3 v2/core/01-mcp-server/mcp_server.py run-extraction'
alias mcp_extraction_status='python3 v2/core/01-mcp-server/mcp_server.py extraction-status'
alias mcp_list_extraction_registries='python3 v2/core/01-mcp-server/mcp_server.py list-extraction-registries'
alias mcp_clear_extraction_data='python3 v2/core/01-mcp-server/mcp_server.py clear-extraction-data'
alias mcp_search_by_category='python3 v2/core/01-mcp-server/mcp_server.py search-by-category'
alias mcp_list_registry_sources='python3 v2/core/01-mcp-server/mcp_server.py list-registry-sources'

# Content Collection Commands (03-content-collection)
alias content_discover='python3 v2/03-content-collection/content_collection_cli.py discover'
alias content_fetch='python3 v2/03-content-collection/content_collection_cli.py fetch'
alias content_status='python3 v2/03-content-collection/content_collection_cli.py status'
alias content_list_source_types='python3 v2/03-content-collection/content_collection_cli.py list-source-types'

# Extractor Commands (04-extractors)
alias extractors_list='python3 v2/04-extractors/extractors_cli.py list'
alias extractors_run='python3 v2/04-extractors/extractors_cli.py run'
alias extractors_run_all='python3 v2/04-extractors/extractors_cli.py run-all'
alias extractors_status='python3 v2/04-extractors/extractors_cli.py status'

# RAG Builder Commands (02-rag-builder)
alias rag_builder_status='python3 v2/02-rag-builder/rag_builder_cli.py status'
alias rag_builder_list_profiles='python3 v2/02-rag-builder/rag_builder_cli.py list-profiles'
alias rag_builder_check='python3 v2/02-rag-builder/rag_builder_cli.py check'

# Test Commands
alias test_registry='python3 v2/core/00-rag-registry/tests/run.py'
alias test_mcp='python3 v2/core/01-mcp-server/tests/run.py'
alias test_content='python3 v2/03-content-collection/tests/run.py'
alias test_extractors='python3 v2/04-extractors/tests/run.py'
alias test_all='python3 v2/tests/run_all.py'

echo "SimFlo RAG v2 command aliases enabled!"
echo "Use 'simflo_help' to see all available commands"
```

## Integration Examples

### AI Assistant Workflow
```bash
# 1. Set up environment
source v2/commands.sh

# 2. Set platform context
mcp_set_context reactjs --session-id ai-assistant-001

# 3. Search for components
mcp_search "form with validation and submit button" --limit 5

# 4. Get component details
mcp_get_component form --registry shadcn

# 5. List related components
mcp_list_components --type ui --platform reactjs --limit 20

# 6. Check system status
simflo_status
```

### Content Processing Workflow
```bash
# 1. System setup
source v2/commands.sh
simflo_setup

# 2. Discover sources
content_discover --query "react component libraries" --source-type github --limit 10

# 3. Fetch content
content_fetch --sources-file sources.json --output-dir raw_content/

# 4. Extract components
extractors_run_all --parallel

# 5. Update registries
rag_registry_rebuild --registry shadcn
rag_registry_rebuild --registry gluestack

# 6. Test search functionality
mcp_search "button component" --limit 10
```

### Development and Testing Workflow
```bash
# 1. Enable aliases
source v2/commands.sh

# 2. Run system tests
simflo_test

# 3. Check component status
rag_registry_status
mcp_extraction_status
extractors_status

# 4. Test specific functionality
mcp_search "button" --limit 5
extractors_run shadcn --source-type github --repository shadcn-ui/ui
rag_registry_search --query "component" --limit 10

# 5. Verify results
simflo_status --detailed
```

## Troubleshooting

### Common Issues

1. **Aliases not found**:
   ```bash
   # Make sure you've sourced the commands file
   source v2/commands.sh

   # Check if file exists
   ls -la v2/commands.sh
   ```

2. **Permission denied**:
   ```bash
   # Make file executable
   chmod +x v2/commands.sh

   # Make Python scripts executable
   chmod +x v2/scripts/*.py
   ```

3. **Path issues**:
   ```bash
   # Use absolute path
   source /full/path/to/simflo-rag/v2/commands.sh

   # Check current directory
   pwd
   ls -la v2/
   ```

### Reset Aliases
```bash
# Disable all SimFlo RAG aliases
unalias simflo_help simflo_setup simflo_status simflo_test
unalias rag_registry_list rag_registry_info rag_registry_search rag_registry_status rag_registry_clean rag_registry_rebuild
unalias mcp_search mcp_get_component mcp_list_components mcp_set_context mcp_get_context mcp_list_registries
unalias mcp_run_extraction mcp_extraction_status mcp_list_extraction_registries mcp_clear_extraction_data
unalias mcp_search_by_category mcp_list_registry_sources
unalias content_discover content_fetch content_status content_list_source_types
unalias extractors_list extractors_run extractors_run_all extractors_status
unalias rag_builder_status rag_builder_list_profiles rag_builder_check
unalias test_registry test_mcp test_content test_extractors test_all
```

### Debug Mode
```bash
# Enable debug output
set -x  # Enable command tracing
source v2/commands.sh

# Test individual commands
which mcp_search
type mcp_search
mcp_search --help

# Disable debug when done
set +x
```

## Customization

### Adding Custom Aliases
```bash
# Add to v2/commands.sh or your shell profile
alias my_search='mcp_search'
alias quick_status='simflo_status'
alias dev_setup='simflo_setup && simflo_status'
```

### Environment-Specific Aliases
```bash
# Development environment
if [[ "$ENV" == "dev" ]]; then
    alias dev_extract='extractors_run_all --parallel --output-dir dev-extracted/'
    alias dev_test='simflo_test && simflo_status'
fi

# Production environment
if [[ "$ENV" == "prod" ]]; then
    alias prod_extract='extractors_run_all --output-dir prod-extracted/'
    alias prod_status='rag_registry_status --detailed'
fi
```

This command alias system provides a convenient and efficient interface for interacting with all SimFlo RAG v2 components, making it easier for both users and AI assistants to navigate and operate the system.