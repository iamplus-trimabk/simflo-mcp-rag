#!/bin/bash
# simflo-rag Command Aliases - Source this file to enable CLI shortcuts
#
# Setup:
#   source commands.sh
#   Or add to ~/.bashrc or ~/.zshrc for persistence:
#   echo 'source /path/to/simflo-mcp-rag/commands.sh' >> ~/.bashrc
#
# Usage:
#   rag_registry list --format json
#   mcp_server search "button" --limit 5
#   extractors list-extractors --format table

echo "🚀 simflo-rag CLI aliases loaded!"
echo "Available commands: rag_registry, mcp_server, rag_builder, content_collection, extractors, test_executor"
echo ""

# Registry Management (00-rag-registry)
alias rag_registry='python3 v2/core/00-rag-registry/registry.py'

# AI Assistant Integration (01-mcp-server)
alias mcp_server='python3 v2/core/01-mcp-server/mcp_server.py'

# Pipeline Orchestration (02-rag-builder)
alias rag_builder='python3 v2/core/02-rag-builder/rag_builder_cli.py'

# Content Discovery & Acquisition (03-content-collection)
alias content_collection='python3 v2/03-content-collection/content_collection_cli.py'

# Content Extraction (04-extractors)
alias extractors='python3 v2/04-extractors/extractors_cli.py'

# Test Execution
alias test_executor='python3 v2/tests/cmd_test_executor.py'

# Quick status check for all components
alias simflo_status='echo "=== RAG Registry Status ===" && rag_registry status --format table && echo "" && echo "=== MCP Server Status ===" && mcp_server list-registries --format table && echo "" && echo "=== Extractors Status ===" && extractors status --format table'

# Help function
simflo_help() {
    echo "simflo-rag CLI Commands:"
    echo ""
    echo "🔧 Core Commands:"
    echo "  rag_registry     - Registry database management (list, search, info, status)"
    echo "  mcp_server       - AI assistant integration (search, get-component, list-components)"
    echo "  rag_builder      - Pipeline orchestration (status, list-profiles, check)"
    echo "  content_collection - Source discovery and acquisition"
    echo "  extractors       - Content extraction from various sources"
    echo "  test_executor    - Run test suites"
    echo ""
    echo "🚀 Quick Commands:"
    echo "  simflo_status    - Show status of all components"
    echo "  simflo_help      - Show this help message"
    echo ""
    echo "📖 Examples:"
    echo "  rag_registry list --format json"
    echo "  mcp_server search \"button\" --limit 5"
    echo "  extractors list-extractors --format table"
    echo "  content_collection discover --query \"react components\""
    echo ""
    echo "💡 Tip: Use --format json or --format table with any command"
}

# Add help to aliases
alias simflo_help='simflo_help'