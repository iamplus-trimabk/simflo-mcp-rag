#!/bin/bash

# SimFlo RAG v2 - Command Aliases System
#
# Purpose: Centralized command aliases for consistent interface and easier usage
# Usage: source v2/commands.sh (or add to shell profile for persistence)
#
# All commands default to JSON format for structured output and AI integration

# Content Root Environment Variable
export CONTENT_ROOT="/Users/tbardale/v2/simflo-mcp-rag/content"

# RAG Registry Commands
alias rag_registry="python3 v2/core/00-rag-registry/registry.py"
alias rag_registry_list="python3 v2/core/00-rag-registry/registry.py list --format json"
alias rag_registry_info="python3 v2/core/00-rag-registry/registry.py info --name"
alias rag_registry_status="python3 v2/core/00-rag-registry/registry.py status --format json"
alias rag_registry_search="python3 v2/core/00-rag-registry/registry.py search --format json"
alias rag_registry_clean="python3 v2/core/00-rag-registry/registry.py clean-db --format json"
alias rag_registry_rebuild="python3 v2/core/00-rag-registry/registry.py rebuild-db --format json"

# MCP Server Commands
alias mcp_server="python3 v2/core/01-mcp-server/mcp_server.py"
alias mcp_search="python3 v2/core/01-mcp-server/mcp_server.py search --format json"
alias mcp_get_component="python3 v2/core/01-mcp-server/mcp_server.py get-component --format json"
alias mcp_list_components="python3 v2/core/01-mcp-server/mcp_server.py list-components --format json"
alias mcp_list_registries="python3 v2/core/01-mcp-server/mcp_server.py list-registries --format json"
alias mcp_set_context="python3 v2/core/01-mcp-server/mcp_server.py set-context --format json"
alias mcp_get_context="python3 v2/core/01-mcp-server/mcp_server.py get-context --format json"

# MCP Server Extraction Commands (Now Implemented!)
alias mcp_run_extraction="python3 v2/core/01-mcp-server/mcp_server.py run-extraction --format json"
alias mcp_extraction_status="python3 v2/core/01-mcp-server/mcp_server.py extraction-status --format json"
alias mcp_list_extraction_registries="python3 v2/core/01-mcp-server/mcp_server.py list-extraction-registries --format json"
alias mcp_clear_extraction_data="python3 v2/core/01-mcp-server/mcp_server.py clear-extraction-data --format json"
alias mcp_search_by_category="python3 v2/core/01-mcp-server/mcp_server.py search-by-category --format json"
alias mcp_list_registry_sources="python3 v2/core/01-mcp-server/mcp_server.py list-registry-sources --format json"

# RAG Builder Commands
alias rag_builder="python3 v2/core/02-rag-builder/rag_builder_cli.py"
alias rag_builder_status="python3 v2/core/02-rag-builder/rag_builder_cli.py status --format json"
alias rag_builder_index="python3 v2/core/02-rag-builder/rag_builder_cli.py index --format json"

# Content Collection Commands
alias content_collection="python3 v2/03-content-collection/content_collection_cli.py"
alias content_discover="python3 v2/03-content-collection/content_collection_cli.py discover --format json"
alias content_fetch="python3 v2/03-content-collection/content_collection_cli.py fetch --format json"
alias content_status="python3 v2/03-content-collection/content_collection_cli.py status --format json"

# Extractors Commands
alias extractors="python3 v2/04-extractors/extractors_cli.py"
alias extractors_list="python3 v2/04-extractors/extractors_cli.py list-extractors --format json"
alias extractors_run="python3 v2/04-extractors/extractors_cli.py run-extractor --format json"
alias extractors_run_all="python3 v2/04-extractors/extractors_cli.py run-all-extractors --format json"
alias extractors_status="python3 v2/04-extractors/extractors_cli.py status --format json"

# Test Commands
alias test_registry="python3 v2/core/00-rag-registry/tests/run.py --verbose"
alias test_mcp="python3 v2/core/01-mcp-server/tests/run.py --verbose"
alias test_content="python3 v2/03-content-collection/tests/run.py --verbose"
alias test_extractors="python3 v2/04-extractors/tests/run.py --verbose"
alias test_all="python3 v2/tests/cmd_test_executor.py v2/core/00-rag-registry/tests/cmd_tests.json && python3 v2/tests/cmd_test_executor.py v2/core/01-mcp-server/tests/mcp_tests.json && python3 v2/tests/cmd_test_executor.py v2/03-content-collection/tests/content_collection_tests.json && python3 v2/tests/cmd_test_executor.py v2/04-extractors/tests/extractor_tests.json"

# Quick Status Commands
alias simflo_status="rag_registry_status && mcp_list_registries && extractors_status"
alias simflo_test="test_registry && test_mcp"

# Helper Functions
simflo_help() {
    echo "SimFlo RAG v2 - Command Aliases (Opinionated: shadcn + gluestack)"
    echo ""
    echo "Core Commands:"
    echo "  rag_registry_*     - Registry management (shadcn + gluestack only)"
    echo "  mcp_*             - MCP server commands (AI assistant integration)"
    echo "  rag_builder_*     - RAG pipeline commands"
    echo "  content_*         - Content collection commands"
    echo "  extractors_*      - Content extraction (GitHub CLI based)"
    echo ""
    echo "Status & Testing:"
    echo "  simflo_status     - Show status across all components"
    echo "  simflo_test       - Run core test suites"
    echo "  test_*            - Individual component test commands"
    echo ""
    echo "Supported Libraries:"
    echo "  shadcn            - Modern React components (shadcn-ui/ui)"
    echo "  gluestack         - Cross-platform React/React Native components"
    echo ""
    echo "Examples:"
    echo "  mcp_search \"button\" --limit 5"
    echo "  rag_registry_search --query \"dialog\""
    echo "  extractors_run shadcn"
    echo "  extractors_run gluestack"
    echo "  simflo_status"
    echo ""
    echo "Environment:"
    echo "  CONTENT_ROOT      - Content storage path (configurable)"
    echo "  GitHub CLI        - Required for repository access (gh command)"
    echo ""
    echo "For AI assistant integration guide: v2/docs/ai-assistant-integration.md"
    echo "For full documentation: v2/CLAUDE.md"
}

# Auto-setup function
simflo_setup() {
    echo "Setting up SimFlo RAG v2 environment..."

    # Test basic functionality
    echo "Testing core components..."
    rag_registry_list > /dev/null 2>&1 && echo "✅ RAG Registry: OK" || echo "❌ RAG Registry: Error"
    mcp_list_registries > /dev/null 2>&1 && echo "✅ MCP Server: OK" || echo "❌ MCP Server: Error"
    extractors_list > /dev/null 2>&1 && echo "✅ Extractors: OK" || echo "❌ Extractors: Error"

    echo ""
    echo "SimFlo RAG v2 environment ready!"
    echo "Use 'simflo_help' for command reference"
}

# Export functions
export -f simflo_help
export -f simflo_setup

echo "SimFlo RAG v2 command aliases loaded"
echo "Type 'simflo_help' for command reference or 'simflo_setup' to test the system"