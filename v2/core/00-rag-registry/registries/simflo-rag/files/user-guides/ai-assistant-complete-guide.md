# AI Assistant Complete Guide to SimFlo RAG v2

## Purpose
Comprehensive guide for AI assistants to learn about, understand, and effectively use SimFlo RAG v2. This guide enables AI assistants to leverage SimFlo RAG tools to get SimFlo RAG work done through a self-documenting system.

## What is SimFlo RAG v2?

SimFlo RAG v2 is a CLI-first, registry-based RAG (Retrieval-Augmented Generation) system that provides comprehensive component discovery, content processing, and knowledge management capabilities. The system is designed to be **self-documenting** - it uses SimFlo RAG to document itself, enabling AI assistants to learn about the system through the system itself.

### Core Philosophy
- **CLI-First Architecture**: All component communication uses structured Python CLI calls
- **Registry-Based Organization**: Content organized in independent registries with vector databases
- **Self-Documenting System**: The system documents itself for AI assistant learning
- **Opinionated Approach**: Focused support for specific, high-quality component libraries

### Key Components (Numbered System)
1. **00-rag-registry**: Registry-based RAG database management
2. **01-mcp-server**: AI assistant integration via CLI (18 commands)
3. **02-rag-builder**: Pipeline orchestration and RAG construction
4. **03-content-collection**: Source discovery and content acquisition
5. **04-extractors**: Content extraction from various sources (11 extractors)

## Getting Started as an AI Assistant

### Quick Start Workflow

1. **Set Platform Context**:
```bash
python3 v2/core/01-mcp-server/mcp_server.py set-context documentation --session-id ai-learning --format json
```

2. **Learn System Architecture**:
```bash
python3 v2/core/01-mcp-server/mcp_server.py search "system architecture overview CLI components" --registry simflo-rag --limit 10 --format json
```

3. **Discover Available Commands**:
```bash
python3 v2/core/01-mcp-server/mcp_server.py search "CLI commands registry operations" --registry simflo-rag --limit 15 --format json
```

4. **Understand Integration Patterns**:
```bash
python3 v2/core/01-mcp-server/mcp_server.py search "AI assistant integration workflow patterns" --registry simflo-rag --limit 10 --format json
```

### Essential Learning Path

#### Step 1: Understand the Architecture
```bash
# Set documentation context
python3 v2/core/01-mcp-server/mcp_server.py set-context documentation --session-id learning-001

# Learn about numbered architecture
python3 v2/core/01-mcp-server/mcp_server.py search "numbered system components CLI first architecture" --registry simflo-rag --limit 5

# Understand CLI philosophy
python3 v2/core/01-mcp-server/mcp_server.py search "CLI first design JSON output structured communication" --registry simflo-rag --limit 5
```

#### Step 2: Master the Registry System
```bash
# Learn registry concepts
python3 v2/core/01-mcp-server/mcp_server.py search "registry-based organization vector databases" --registry simflo-rag --limit 8

# Understand registry operations
python3 v2/core/01-mcp-server/mcp_server.py search "registry CLI commands list search rebuild" --registry simflo-rag --limit 10

# Learn database management
python3 v2/core/01-mcp-server/mcp_server.py search "DatabaseManager standardized paths cleanup operations" --registry simflo-rag --limit 8
```

#### Step 3: Explore MCP Server Capabilities
```bash
# Learn MCP server functionality
python3 v2/core/01-mcp-server/mcp_server.py search "MCP server 18 commands AI assistant integration" --registry simflo-rag --limit 10

# Understand search capabilities
python3 v2/core/01-mcp-server/mcp_server.py search "component search natural language queries platform context" --registry simflo-rag --limit 8

# Master context management
python3 v2/core/01-mcp-server/mcp_server.py search "set-context get-context platform context session management" --registry simflo-rag --limit 6
```

#### Step 4: Learn Content Processing Pipeline
```bash
# Understand content collection
python3 v2/core/01-mcp-server/mcp_server.py search "content collection source discovery GitHub CLI" --registry simflo-rag --limit 8

# Learn extraction system
python3 v2/core/01-mcp-server/mcp_server.py search "specialized extractors shadcn gluestack content extraction" --registry simflo-rag --limit 10

# Master pipeline integration
python3 v2/core/01-mcp-server/mcp_server.py search "content processing pipeline discovery extraction registry" --registry simflo-rag --limit 8
```

## Core Capabilities for AI Assistants

### 1. Component Discovery and Recommendation

#### Search Components for User Requirements
```bash
# Set appropriate platform context
python3 v2/core/01-mcp-server/mcp_server.py set-context reactjs --session-id user-assistance-001

# Search for components based on requirements
python3 v2/core/01-mcp-server/mcp_server.py search "form with validation and submit button" --limit 5 --format json

# Get detailed component information
python3 v2/core/01-mcp-server/mcp_server.py get-component form --registry shadcn --format json

# List related components
python3 v2/core/01-mcp-server/mcp_server.py list-components --type ui --platform reactjs --limit 20 --format json
```

#### Intelligent Component Recommendations
```bash
# React JS context
python3 v2/core/01-mcp-server/mcp_server.py set-context reactjs --session-id web-development
python3 v2/core/01-mcp-server/mcp_server.py search "card component with image and text" --limit 8

# React Native context
python3 v2/core/01-mcp-server/mcp_server.py set-context reactnative --session-id mobile-development
python3 v2/core/01-mcp-server/mcp_server.py search "bottom navigation with tabs and icons" --limit 5

# Documentation context (for learning)
python3 v2/core/01-mcp-server/mcp_server.py set-context documentation --session-id self-learning
python3 v2/core/01-mcp-server/mcp_server.py search "registry system CLI commands database management" --registry simflo-rag --limit 15
```

### 2. System Operation and Management

#### Monitor System Health
```bash
# Check overall system status
python3 v2/core/00-rag-registry/registry.py status --format json

# Check MCP server operational status
python3 v2/core/01-mcp-server/mcp_server.py extraction-status --format json

# Verify extractor system functionality
python3 v2/04-extractors/extractors_cli.py status --detailed --format json

# Test content collection capabilities
python3 v2/03-content-collection/content_collection_cli.py status --format json
```

#### Registry Management Operations
```bash
# List available registries
python3 v2/core/01-mcp-server/mcp_server.py list-registries --format json

# Get detailed registry information
python3 v2/core/00-rag-registry/registry.py info --name shadcn --format json

# Search across all registries
python3 v2/core/00-rag-registry/registry.py search --query "button component" --limit 10 --format json

# Rebuild registry database (if needed)
python3 v2/core/00-rag-registry/registry.py rebuild-db --registry shadcn --format json
```

### 3. Content Processing and Knowledge Management

#### Process New Content Sources
```bash
# Discover relevant sources
python3 v2/03-content-collection/content_collection_cli.py discover --query "react dashboard components" --source-type github --limit 10 --format json

# Fetch content from discovered sources
python3 v2/03-content-collection/content_collection_cli.py fetch --sources-file discovered_sources.json --output-dir raw_content/ --format json

# Extract structured content
python3 v2/04-extractors/extractors_cli.py run-all --parallel --output-dir extracted/ --format json

# Update registries with new content
python3 v2/core/00-rag-registry/registry.py rebuild-db --registry shadcn --format json
```

#### Manage Knowledge Base
```bash
# Run extraction for specific registry
python3 v2/core/01-mcp-server/mcp_server.py run-extraction --registry shadcn --mode test --format json

# Clear extraction data if needed
python3 v2/core/01-mcp-server/mcp_server.py clear-extraction-data --registry shadcn --format json

# Search within specific categories
python3 v2/core/01-mcp-server/mcp_server.py search-by-category "form" components --format json
python3 v2/core/01-mcp-server/mcp_server.py search-by-category "validation" hooks --format json
```

## Advanced AI Assistant Workflows

### Workflow 1: Helping Users with Component Selection

```bash
# 1. Understand user's project context
python3 v2/core/01-mcp-server/mcp_server.py set-context reactjs --session-id user-project-001 --project-type "dashboard" --format json

# 2. Search for relevant components
python3 v2/core/01-mcp-server/mcp_server.py search "data table with sorting pagination and filtering" --limit 8 --format json

# 3. Get detailed information about top recommendations
python3 v2/core/01-mcp-server/mcp_server.py get-component table --registry shadcn --format json
python3 v2/core/01-mcp-server/mcp_server.py get-component pagination --registry shadcn --format json

# 4. List related components for complete solution
python3 v2/core/01-mcp-server/mcp_server.py list-components --type ui --platform reactjs --limit 20 --format json

# 5. Provide comprehensive recommendation
# (Use the gathered information to provide detailed recommendations with installation instructions, usage examples, and integration guidance)
```

### Workflow 2: Learning About SimFlo RAG System

```bash
# 1. Set learning context
python3 v2/core/01-mcp-server/mcp_server.py set-context documentation --session-id ai-learning --format json

# 2. Learn system architecture
python3 v2/core/01-mcp-server/mcp_server.py search "SimFlo RAG v2 architecture numbered components CLI first" --registry simflo-rag --limit 10 --format json

# 3. Understand core functionality
python3 v2/core/01-mcp-server/mcp_server.py search "registry system database management vector search" --registry simflo-rag --limit 8 --format json

# 4. Learn CLI capabilities
python3 v2/core/01-mcp-server/mcp_server.py search "MCP server 18 commands search get-component list-components" --registry simflo-rag --limit 12 --format json

# 5. Master integration patterns
python3 v2/core/01-mcp-server/mcp_server.py search "AI assistant integration context management workflow" --registry simflo-rag --limit 10 --format json

# 6. Explore advanced features
python3 v2/core/01-mcp-server/mcp_server.py search "content collection extraction pipeline GitHub CLI" --registry simflo-rag --limit 8 --format json
```

### Workflow 3: System Maintenance and Troubleshooting

```bash
# 1. Check system health
python3 v2/core/00-rag-registry/registry.py status --format json
python3 v2/core/01-mcp-server/mcp_server.py extraction-status --format json
python3 v2/04-extractors/extractors_cli.py status --detailed --format json

# 2. Identify issues
python3 v2/core/01-mcp-server/mcp_server.py search "troubleshooting error handling common issues" --registry simflo-rag --limit 10 --format json

# 3. Apply fixes
python3 v2/core/00-rag-registry/registry.py rebuild-db --registry problematic-registry --format json
python3 v2/04-extractors/extractors_cli.py run failing-extractor --source-type local --source-path /path/to/source --output-dir extracted/ --format json

# 4. Verify fixes
python3 v2/core/00-rag-registry/registry.py search --query "test query" --limit 5 --format json
python3 v2/core/01-mcp-server/mcp_server.py search "test component" --limit 3 --format json
```

## Command Reference for AI Assistants

### Essential Commands for Daily Operations

#### Context Management
```bash
# Set context for intelligent recommendations
set-context [platform] --session-id [id]

# Get current context
get-context --session-id [id]
```

#### Component Discovery
```bash
# Search components
search "[query]" --limit [number] --platform [platform]

# Get component details
get-component [name] --registry [registry]

# List components
list-components --type [type] --platform [platform] --limit [number]
```

#### System Information
```bash
# List available registries
list-registries --platform [platform]

# Get system status
rag_registry_status
extraction-status
```

#### Learning and Documentation
```bash
# Search SimFlo RAG documentation
search "[topic]" --registry simflo-rag --limit [number]

# Get detailed information
get-component "[document-name]" --registry simflo-rag
```

### Command Output Interpretation

#### Success Response Structure
```json
{
  "success": true,
  "timestamp": "2025-09-30T21:37:01.043963",
  "data": {
    // Command-specific data
    "query": "button component",
    "total_found": 25,
    "results": [...]
  }
}
```

#### Error Response Structure
```json
{
  "success": false,
  "timestamp": "2025-09-30T21:37:01.043963",
  "error": "Registry 'unknown' not found",
  "error_code": "REGISTRY_NOT_FOUND",
  "suggestions": ["Use 'list-registries' to see available registries"]
}
```

## Best Practices for AI Assistants

### 1. Always Set Appropriate Context
```bash
# Before any component search, set the platform context
python3 v2/core/01-mcp-server/mcp_server.py set-context reactjs --session-id [unique-session-id]

# For learning about SimFlo RAG, use documentation context
python3 v2/core/01-mcp-server/mcp_server.py set-context documentation --session-id [learning-session-id]
```

### 2. Use Natural Language Queries
```bash
# Good: Specific, descriptive queries
search "form with client-side validation and error messages"
search "responsive navigation menu with dropdown and mobile support"
search "data table with server-side pagination and sorting"

# Avoid: Vague or single-word queries
search "form"
search "menu"
search "table"
```

### 3. Leverage the Self-Documenting System
```bash
# When you need to understand any aspect of SimFlo RAG
search "[topic]" --registry simflo-rag

# Examples:
search "how to rebuild registry database" --registry simflo-rag
search "extraction system status monitoring" --registry simflo-rag
search "command aliases setup and usage" --registry simflo-rag
```

### 4. Provide Comprehensive Assistance
When helping users:
1. **Set appropriate context** for their project
2. **Search for relevant components** using natural language
3. **Get detailed information** about top recommendations
4. **Provide installation instructions** and usage examples
5. **Suggest related components** for complete solutions

### 5. Handle Errors Gracefully
When encountering errors:
1. **Check system status** to identify issues
2. **Search for troubleshooting information** in simflo-rag registry
3. **Suggest specific fixes** based on error codes
4. **Verify fixes** by re-running affected commands

## Integration with External Tools

### Command Aliases for Enhanced Productivity
```bash
# Setup command aliases (source v2/commands.sh)
source v2/commands.sh

# Use convenient aliases for common operations
mcp_search "button component" --limit 10
mcp_get_component form --registry shadcn
rag_registry_status
extractors_run shadcn
```

### Pipeline Integration
```bash
# Complete content processing pipeline
content_discover --query "react components" --source-type github --limit 5 | \
content_fetch --sources - --output-dir raw_content/ | \
extractors_run_all --parallel --output-dir extracted/ | \
rag_registry_rebuild --registry shadcn
```

## Learning Resources

### Self-Guided Learning Path

1. **Start with Architecture**: Understand the numbered system and CLI-first design
2. **Master Registry System**: Learn database management and search operations
3. **Explore MCP Server**: Understand all 18 commands and AI integration patterns
4. **Study Content Processing**: Learn collection, extraction, and pipeline operations
5. **Practice Integration**: Use real workflows to assist users and manage the system

### Continuous Learning

The simflo-rag registry is continuously updated with the latest documentation, commands, and best practices. Regularly search for new content to stay current:

```bash
# Search for latest updates and features
search "new features updates latest version" --registry simflo-rag --limit 10

# Learn best practices and patterns
search "best practices patterns recommendations" --registry simflo-rag --limit 15

# Explore advanced capabilities
search "advanced features expert usage optimization" --registry simflo-rag --limit 10
```

## Troubleshooting Common Issues

### Component Search Issues
```bash
# If no components found, check:
# 1. Available registries
list-registries

# 2. Current context
get-context

# 3. Search query specificity
search "more specific description of what you need" --limit 10
```

### System Status Issues
```bash
# Check overall system health
rag_registry_status --detailed
extraction-status --detailed
extractors_status --detailed

# Search for troubleshooting help
search "troubleshooting system issues errors" --registry simflo-rag --limit 10
```

### Performance Issues
```bash
# Use parallel processing when available
extractors_run_all --parallel
content_fetch --parallel

# Monitor resource usage
rag_registry_status --detailed
```

This comprehensive guide enables AI assistants to effectively learn about, understand, and use SimFlo RAG v2 to assist users and manage the system through the power of its self-documenting architecture.