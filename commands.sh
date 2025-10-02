#!/bin/bash

# SimFlo RAG v2 - Command Aliases System
#
# Purpose: Centralized command aliases for consistent interface and easier usage
# Usage: source commands.sh (or add to shell profile for persistence)
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

# Universal Repository Extraction Commands (NEW!)
alias extractors_detect="python3 v2/04-extractors/extractors_cli.py detect-repository --format json"
alias extractors_extract="python3 v2/04-extractors/extractors_cli.py extract-repository --format json"
alias extractors_extract_all="python3 v2/04-extractors/extractors_cli.py extract-all-applicable --format json"

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
    echo "🚀 SimFlo RAG Commands (sm_ prefix):"
    echo "  sm_learn          - Learn SimFlo RAG architecture (self-documenting)"
    echo "  sm_guide          - Get AI assistant complete guide"
    echo "  sm_commands       - Get CLI commands reference"
    echo "  sm_search \"query\" - Search SimFlo RAG documentation"
    echo "  sm_get \"doc-name\" - Get specific documentation"
    echo "  sm_registries     - List all registries (including simflo-rag)"
    echo ""
    echo "🔧 Core Commands:"
    echo "  rag_registry_*     - Registry management (shadcn + gluestack only)"
    echo "  mcp_*             - MCP server commands (AI assistant integration)"
    echo "  rag_builder_*     - RAG pipeline commands"
    echo "  content_*         - Content collection commands"
    echo "  extractors_*      - Content extraction (GitHub CLI + Universal repository support)"
    echo ""
    echo "📊 Status & Testing:"
    echo "  simflo_status     - Show status across all components"
    echo "  simflo_test       - Run core test suites"
    echo "  test_*            - Individual component test commands"
    echo ""
    echo "📚 Supported Libraries:"
    echo "  shadcn            - Modern React components (shadcn-ui/ui)"
    echo "  gluestack         - Cross-platform React/React Native components"
    echo ""
    echo "💡 Examples:"
    echo "  sm_learn                    # Learn about SimFlo RAG"
    echo "  sm_search \"architecture\"    # Search architecture docs"
    echo "  sm_get \"ai-assistant-complete-guide\" --registry simflo-rag"
    echo "  mcp_search \"button\" --limit 5"
    echo "  extractors_run shadcn"
    echo "  extractors_detect --repository-url \"https://github.com/microsoft/TypeScript\""
    echo "  extractors_extract --repository-url \"https://github.com/testing-library/jest-dom\""
    echo "  simflo_status"
    echo ""
    echo "🌍 Environment:"
    echo "  CONTENT_ROOT      - Content storage path (configurable)"
    echo "  GitHub CLI        - Required for repository access (gh command)"
    echo ""
    echo "📖 For AI assistant integration guide: v2/docs/ai-assistant-integration.md"
    echo "📖 For full documentation: v2/CLAUDE.md"
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

# SimFlo RAG Specific Commands (sm_ prefix)
alias sm_search="python3 v2/core/01-mcp-server/mcp_server.py search --format json"
alias sm_get="python3 v2/core/01-mcp-server/mcp_server.py get-component --format json"
alias sm_list="python3 v2/core/01-mcp-server/mcp_server.py list-components --format json"
alias sm_registries="python3 v2/core/01-mcp-server/mcp_server.py list-registries --format json"
alias sm_set_context="python3 v2/core/01-mcp-server/mcp_server.py set-context --format json"
alias sm_get_context="python3 v2/core/01-mcp-server/mcp_server.py get-context --format json"

# SimFlo RAG Self-Documentation Commands
alias sm_learn="python3 v2/core/01-mcp-server/mcp_server.py get-component simflo-rag-complete-architecture --registry simflo-rag --format json"
alias sm_guide="python3 v2/core/01-mcp-server/mcp_server.py get-component ai-assistant-complete-guide --registry simflo-rag --format json"
alias sm_commands="python3 v2/core/01-mcp-server/mcp_server.py get-component cli-commands-complete-reference --registry simflo-rag --format json"

# SimFlo RAG Registry Management Commands
alias sm_create_registry="python3 v2/core/00-rag-registry/registry.py create --format json"
alias sm_rebuild_registry="python3 v2/core/00-rag-registry/registry.py rebuild-db --format json"
alias sm_list_registry_info="python3 v2/core/00-rag-registry/registry.py info --format json"
alias sm_registry_status="python3 v2/core/00-rag-registry/registry.py status --format json"

# SimFlo RAG Content Processing Commands
alias sm_discover_content="python3 v2/core/03-content-collection/content_collection_cli.py discover --format json"
alias sm_fetch_content="python3 v2/core/03-content-collection/content_collection_cli.py fetch --format json"
alias sm_run_extractors="python3 v2/04-extractors/extractors_cli.py run-all-extractors --format json"
alias sm_extract_pdf="python3 v2/04-extractors/extractors_cli.py run-extractor pdf-extractor --format json"

# AI Assistant Quick Start Function
sm_ai_help() {
    echo "SimFlo RAG v2 - AI Assistant Quick Start"
    echo ""
    echo "🎓 Learn SimFlo RAG (Self-Documenting System):"
    echo "  sm_learn          - Get complete system architecture"
    echo "  sm_guide          - Get AI assistant comprehensive guide"
    echo "  sm_commands       - Get complete CLI command reference"
    echo ""
    echo "🔍 Search Documentation:"
    echo "  sm_search \"architecture\" --limit 5      # Search architecture docs"
    echo "  sm_search \"CLI commands\" --limit 10     # Search command reference"
    echo "  sm_search \"registry system\"             # Search registry info"
    echo ""
    echo "📄 Get Specific Documents:"
    echo "  sm_get \"ai-assistant-complete-guide\" --registry simflo-rag"
    echo "  sm_get \"setup-and-installation-guide\" --registry simflo-rag"
    echo "  sm_get \"simflo-rag-complete-architecture\" --registry simflo-rag"
    echo ""
    echo "🔧 Registry Operations:"
    echo "  sm_registries     - List all registries (includes simflo-rag)"
    echo "  sm_list --type ui --platform reactjs    # List UI components"
    echo ""
    echo "💡 Example AI Assistant Workflow:"
    echo "  1. sm_learn                    # Learn about SimFlo RAG"
    echo "  2. sm_search \"registry\"        # Search for registry info"
    echo "  3. sm_get \"ai-assistant-complete-guide\"  # Get detailed guide"
    echo "  4. sm_registries               # See available registries"
    echo ""
    echo "✨ The 'sm_' prefix indicates SimFlo RAG specific commands"
    echo "📖 All commands output JSON for easy AI integration"
}

# Export functions
export -f simflo_help
export -f simflo_setup
export -f sm_ai_help

echo "SimFlo RAG v2 command aliases loaded"
echo "Type 'simflo_help' for command reference, 'sm_ai_help' for AI assistant guide, or 'simflo_setup' to test the system"