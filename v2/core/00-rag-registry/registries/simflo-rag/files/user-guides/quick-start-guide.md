# SimFlo RAG v2 - Quick Start Guide

## Purpose
Quick start guide for AI assistants to immediately begin using SimFlo RAG v2 effectively. Get up and running in 5 minutes with essential commands and workflows.

## 5-Minute Quick Start

### Step 1: Set Your Context
```bash
# For React development help
python3 v2/core/01-mcp-server/mcp_server.py set-context reactjs --session-id my-session-001

# For React Native development help
python3 v2/core/01-mcp-server/mcp_server.py set-context reactnative --session-id my-session-001

# For learning about SimFlo RAG
python3 v2/core/01-mcp-server/mcp_server.py set-context documentation --session-id learning-001
```

### Step 2: Search for Components
```bash
# Find UI components
python3 v2/core/01-mcp-server/mcp_server.py search "button with variants" --limit 5

# Find form components
python3 v2/core/01-mcp-server/mcp_server.py search "form with validation" --limit 8

# Find layout components
python3 v2/core/01-mcp-server/mcp_server.py search "responsive sidebar navigation" --limit 5
```

### Step 3: Get Component Details
```bash
# Get detailed information
python3 v2/core/01-mcp-server/mcp_server.py get-component button --registry shadcn

# List available components
python3 v2/core/01-mcp-server/mcp_server.py list-components --type ui --limit 20
```

### Step 4: Learn About SimFlo RAG
```bash
# Understand the system
python3 v2/core/01-mcp-server/mcp_server.py search "system architecture overview" --registry simflo-rag --limit 5

# Find available commands
python3 v2/core/01-mcp-server/mcp_server.py search "CLI commands reference" --registry simflo-rag --limit 10
```

## Essential Commands Cheat Sheet

### Help and Discovery
```bash
# List available registries
python3 v2/core/01-mcp-server/mcp_server.py list-registries

# Get system status
python3 v2/core/00-rag-registry/registry.py status

# Learn about SimFlo RAG
python3 v2/core/01-mcp-server/mcp_server.py search "getting started guide" --registry simflo-rag
```

### Component Search
```bash
# Search components
python3 v2/core/01-mcp-server/mcp_server.py search "[what you need]" --limit 10

# Get component details
python3 v2/core/01-mcp-server/mcp_server.py get-component [component-name]

# List components by type
python3 v2/core/01-mcp-server/mcp_server.py list-components --type ui --limit 20
```

### Context Management
```bash
# Set React context
python3 v2/core/01-mcp-server/mcp_server.py set-context reactjs --session-id [unique-id]

# Set React Native context
python3 v2/core/01-mcp-server/mcp_server.py set-context reactnative --session-id [unique-id]

# Check current context
python3 v2/core/01-mcp-server/mcp_server.py get-context
```

## Common Workflows

### Helping Users Find Components
```bash
# 1. Set appropriate context
python3 v2/core/01-mcp-server/mcp_server.py set-context reactjs --session-id user-help-001

# 2. Search for what they need
python3 v2/core/01-mcp-server/mcp_server.py search "modal dialog with form and buttons" --limit 5

# 3. Get details about top results
python3 v2/core/01-mcp-server/mcp_server.py get-component dialog --registry shadcn

# 4. Provide installation and usage help
# (Use the information from get-component to provide specific guidance)
```

### Learning About SimFlo RAG
```bash
# 1. Set documentation context
python3 v2/core/01-mcp-server/mcp_server.py set-context documentation --session-id learning-001

# 2. Learn the basics
python3 v2/core/01-mcp-server/mcp_server.py search "what is SimFlo RAG" --registry simflo-rag --limit 5

# 3. Understand the architecture
python3 v2/core/01-mcp-server/mcp_server.py search "numbered system components" --registry simflo-rag --limit 5

# 4. Master the commands
python3 v2/core/01-mcp-server/mcp_server.py search "essential CLI commands" --registry simflo-rag --limit 10
```

### System Health Check
```bash
# Check if everything is working
python3 v2/core/00-rag-registry/registry.py status
python3 v2/core/01-mcp-server/mcp_server.py extraction-status

# Test basic functionality
python3 v2/core/01-mcp-server/mcp_server.py search "button" --limit 3
```

## Quick Examples

### Example 1: Helping a User Build a Form
```bash
# Set React context
python3 v2/core/01-mcp-server/mcp_server.py set-context reactjs --session-id form-help

# Search for form components
python3 v2/core/01-mcp-server/mcp_server.py search "form input validation submit button" --limit 8

# Get details about form component
python3 v2/core/01-mcp-server/mcp_server.py get-component form --registry shadcn

# Get details about input component
python3 v2/core/01-mcp-server/mcp_server.py get-component input --registry shadcn

# Get details about button component
python3 v2/core/01-mcp-server/mcp_server.py get-component button --registry shadcn
```

### Example 2: Finding Navigation Components
```bash
# Set React context
python3 v2/core/01-mcp-server/mcp_server.py set-context reactjs --session-id nav-help

# Search for navigation
python3 v2/core/01-mcp-server/mcp_server.py search "navigation menu with dropdown responsive" --limit 6

# List all UI components
python3 v2/core/01-mcp-server/mcp_server.py list-components --type ui --limit 30
```

### Example 3: Learning SimFlo RAG Commands
```bash
# Set documentation context
python3 v2/core/01-mcp-server/mcp_server.py set-context documentation --session-id cmd-learning

# Search for command reference
python3 v2/core/01-mcp-server/mcp_server.py search "CLI commands complete reference" --registry simflo-rag --limit 10

# Learn about registry commands
python3 v2/core/01-mcp-server/mcp_server.py search "registry CLI commands" --registry simflo-rag --limit 8

# Learn about MCP server commands
python3 v2/core/01-mcp-server/mcp_server.py search "MCP server commands" --registry simflo-rag --limit 8
```

## Output Format Tips

### All commands return JSON with this structure:
```json
{
  "success": true,
  "timestamp": "2025-09-30T21:37:01.043963",
  "data": {
    // Your results here
  }
}
```

### For human-readable output, add `--format table`:
```bash
python3 v2/core/01-mcp-server/mcp_server.py list-components --format table
python3 v2/core/00-rag-registry/registry.py list --format table
```

## Troubleshooting Quick Fixes

### No Components Found?
```bash
# Check available registries
python3 v2/core/01-mcp-server/mcp_server.py list-registries

# Use more specific search terms
python3 v2/core/01-mcp-server/mcp_server.py search "specific description of component" --limit 10

# Check your context
python3 v2/core/01-mcp-server/mcp_server.py get-context
```

### Command Not Working?
```bash
# Check system status
python3 v2/core/00-rag-registry/registry.py status

# Learn troubleshooting
python3 v2/core/01-mcp-server/mcp_server.py search "troubleshooting common issues" --registry simflo-rag --limit 10
```

### Need Help with SimFlo RAG?
```bash
# Search for help in the simflo-rag registry
python3 v2/core/01-mcp-server/mcp_server.py search "help documentation getting started" --registry simflo-rag --limit 10
```

## Next Steps

1. **Practice the basic commands** - Get comfortable with search, get-component, and list-components
2. **Learn about contexts** - Understand how platform context improves recommendations
3. **Explore the simflo-rag registry** - Use `--registry simflo-rag` to learn about the system itself
4. **Try the workflows** - Use the common workflows to help users and learn the system
5. **Read the complete guide** - Check the AI Assistant Complete Guide for comprehensive information

## Key Things to Remember

- **Always set context first** - `set-context reactjs` or `set-context documentation`
- **Use natural language searches** - Describe what you need in detail
- **Check the simflo-rag registry** - Use `--registry simflo-rag` to learn about the system
- **All output is JSON** - Structured data for easy processing
- **Use unique session IDs** - Helps track conversations and context

You're now ready to use SimFlo RAG v2 effectively! Start with the basic commands and gradually explore more advanced features as you become comfortable with the system.