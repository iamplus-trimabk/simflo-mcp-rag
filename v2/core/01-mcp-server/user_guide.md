# MCP Server CLI User Guide

## Quick Start

The MCP Server CLI provides a comprehensive command-line interface for AI assistants to search, discover, and interact with component registries. This guide covers all available commands with practical examples.

### Basic Usage Pattern

```bash
python3 v2/core/01-mcp-server/mcp_server.py <command> [arguments] --format json
```

All commands support `--format json` (default) and `--format table` output formats.

## Command Reference

### Component Search & Discovery

#### search - Search for components

Search for components using natural language queries with optional platform filtering.

```bash
# Basic search
python3 v2/core/01-mcp-server/mcp_server.py search "button" --limit 5

# Search with platform context
python3 v2/core/01-mcp-server/mcp_server.py search "modal dialog" --platform reactjs --limit 10

# Search with table output
python3 v2/core/01-mcp-server/mcp_server.py search "form input validation" --format table
```

**Output Example:**
```json
{
  "success": true,
  "timestamp": "2025-09-30T21:37:55.806146",
  "data": {
    "query": "button",
    "platform": "reactjs",
    "total_found": 3,
    "components": [
      {
        "name": "button",
        "type": "component",
        "registry": "shadcn",
        "relevance_score": 0.95,
        "platform_relevance": 1.0,
        "description": "Accessible button component with variants"
      }
    ]
  }
}
```

#### get-component - Get component details

Retrieve detailed information about a specific component.

```bash
# Get component from any registry
python3 v2/core/01-mcp-server/mcp_server.py get-component button

# Get component from specific registry
python3 v2/core/01-mcp-server/mcp_server.py get-component dialog --registry shadcn

# Get component with table output
python3 v2/core/01-mcp-server/mcp_server.py get-component input --format table
```

**Output Example:**
```json
{
  "success": true,
  "timestamp": "2025-09-30T21:37:01.043963",
  "data": {
    "name": "button",
    "type": "component",
    "description": "Accessible button component with multiple variants",
    "registry": "shadcn",
    "platform": ["reactjs"],
    "dependencies": ["@radix-ui/react-slot"],
    "install_command": "npx shadcn-ui@latest add button",
    "usage_examples": [
      "import { Button } from \"@/components/ui/button\"",
      "<Button>Click me</Button>"
    ]
  }
}
```

#### list-components - List available components

List components from registries with filtering options.

```bash
# List all components
python3 v2/core/01-mcp-server/mcp_server.py list-components --limit 20

# List UI components only
python3 v2/core/01-mcp-server/mcp_server.py list-components --type ui --limit 10

# List components from specific registry with platform filter
python3 v2/core/01-mcp-server/mcp_server.py list-components --registry shadcn --platform reactjs
```

**Output Example:**
```json
{
  "success": true,
  "timestamp": "2025-09-30T21:37:01.043963",
  "data": {
    "type": "ui",
    "registry": "shadcn",
    "platform": "reactjs",
    "total_count": 25,
    "components": [
      {
        "name": "button",
        "type": "ui",
        "description": "Button component with variants"
      },
      {
        "name": "dialog",
        "type": "ui",
        "description": "Modal dialog component"
      }
    ]
  }
}
```

### Context Management

#### set-context - Set platform context

Set platform context for intelligent component recommendations.

```bash
# Set React JS context
python3 v2/core/01-mcp-server/mcp_server.py set-context reactjs

# Set context with session tracking
python3 v2/core/01-mcp-server/mcp_server.py set-context reactnative --session-id mobile-app-123

# Set context with project information
python3 v2/core/01-mcp-server/mcp_server.py set-context reactjs --session-id webapp-456 --project-type "dashboard"
```

**Output Example:**
```json
{
  "success": true,
  "timestamp": "2025-09-30T21:37:01.043963",
  "data": {
    "platform": "reactjs",
    "session_id": "webapp-456",
    "project_type": "dashboard",
    "timestamp": 1696090621,
    "confidence": 0.95,
    "user_agent": "MCP Server CLI"
  }
}
```

#### get-context - Get current platform context

Retrieve the current platform context and session information.

```bash
# Get current context
python3 v2/core/01-mcp-server/mcp_server.py get-context

# Get context for specific session
python3 v2/core/01-mcp-server/mcp_server.py get-context --session-id mobile-app-123
```

**Output Example:**
```json
{
  "success": true,
  "timestamp": "2025-09-30T21:37:01.043963",
  "data": {
    "platform": "reactjs",
    "session_id": "webapp-456",
    "project_type": "dashboard",
    "timestamp": 1696090621,
    "confidence": 0.95
  }
}
```

### Registry Management

#### list-registries - List available registries

List all available component registries with optional platform filtering.

```bash
# List all registries
python3 v2/core/01-mcp-server/mcp_server.py list-registries

# List React JS registries only
python3 v2/core/01-mcp-server/mcp_server.py list-registries --platform reactjs

# List registries with table output
python3 v2/core/01-mcp-server/mcp_server.py list-registries --format table
```

**Output Example:**
```json
{
  "success": true,
  "timestamp": "2025-09-30T21:37:01.043963",
  "data": {
    "platform": null,
    "total_registries": 4,
    "registries": [
      {
        "name": "shadcn",
        "path": "rag_databases/shadcn",
        "platform": ["reactjs"],
        "description": "Component registry for shadcn",
        "component_count": 80,
        "is_active": true,
        "registry_type": "component"
      },
      {
        "name": "gluestack_db",
        "path": "rag_databases/gluestack_db",
        "platform": ["react-native", "reactjs"],
        "description": "Component registry for gluestack",
        "component_count": 28,
        "is_active": true,
        "registry_type": "component"
      }
    ]
  }
}
```

### Extraction Management (Not Implemented)

These commands are included for API compatibility but return "not implemented" messages:

- `run-extraction` - Run extraction pipeline
- `extraction-status` - Get extraction pipeline status
- `list-extraction-registries` - List extraction registries
- `clear-extraction-data` - Clear extracted data
- `search-by-category` - Search by category
- `list-registry-sources` - List registry sources

## AI Assistant Integration Patterns

### Basic Component Discovery Workflow

```bash
# 1. Set platform context for relevant recommendations
python3 v2/core/01-mcp-server/mcp_server.py set-context reactjs --session-id ai-session-001

# 2. Search for components based on requirements
python3 v2/core/01-mcp-server/mcp_server.py search "form with validation and submit button" --limit 5

# 3. Get detailed information about specific components
python3 v2/core/01-mcp-server/mcp_server.py get-component form --registry shadcn

# 4. List related components
python3 v2/core/01-mcp-server/mcp_server.py list-components --type ui --platform reactjs
```

### Advanced Query Examples

```bash
# Search for modal dialog components
python3 v2/core/01-mcp-server/mcp_server.py search "modal dialog with overlay and close button"

# Search for navigation components
python3 v2/core/01-mcp-server/mcp_server.py search "navigation menu with dropdown and responsive design"

# Search for data display components
python3 v2/core/01-mcp-server/mcp_server.py search "data table with sorting and pagination"
```

### Context-Aware Recommendations

```bash
# React Native context
python3 v2/core/01-mcp-server/mcp_server.py set-context reactnative --session-id mobile-dev
python3 v2/core/01-mcp-server/mcp_server.py search "bottom navigation with tabs"

# Auto-detect context
python3 v2/core/01-mcp-server/mcp_server.py set-context auto --project-type "mobile app"
python3 v2/core/01-mcp-server/mcp_server.py search "card component with image and text"
```

## Output Format Reference

### Success Response Structure

```json
{
  "success": true,
  "timestamp": "2025-09-30T21:37:01.043963",
  "data": {
    // Command-specific data
  }
}
```

### Error Response Structure

```json
{
  "success": false,
  "timestamp": "2025-09-30T21:37:01.043963",
  "data": {
    "error": "Error message describing what went wrong"
  }
}
```

### Component Object Structure

```json
{
  "name": "component-name",
  "type": "component",
  "description": "Component description",
  "registry": "registry_name",
  "platform": ["reactjs"],
  "dependencies": ["dependency1", "dependency2"],
  "install_command": "npx shadcn-ui@latest add component-name",
  "usage_examples": [
    "import { Component } from '@/components/ui/component'",
    "<Component>Example usage</Component>"
  ],
  "relevance_score": 0.95,
  "platform_relevance": 1.0
}
```

## Common Use Cases

### 1. Setting Up a New React Project

```bash
# Set React JS context
python3 v2/core/01-mcp-server/mcp_server.py set-context reactjs --session-id new-project

# Find essential UI components
python3 v2/core/01-mcp-server/mcp_server.py search "button input form dialog" --limit 10

# Get installation details for chosen components
python3 v2/core/01-mcp-server/mcp_server.py get-component button
python3 v2/core/01-mcp-server/mcp_server.py get-component form
```

### 2. Mobile App Component Discovery

```bash
# Set React Native context
python3 v2/core/01-mcp-server/mcp_server.py set-context reactnative --session-id mobile-app

# Find mobile-specific components
python3 v2/core/01-mcp-server/mcp_server.py search "bottom tab navigation with icons" --platform reactnative

# List all available mobile components
python3 v2/core/01-mcp-server/mcp_server.py list-components --platform reactnative
```

### 3. Component Library Exploration

```bash
# Explore what's available in shadcn
python3 v2/core/01-mcp-server/mcp_server.py list-registries --platform reactjs

# Browse shadcn components
python3 v2/core/01-mcp-server/mcp_server.py list-components --registry shadcn --type ui

# Search for specific patterns
python3 v2/core/01-mcp-server/mcp_server.py search "accessible form components" --registry shadcn
```

## Troubleshooting

### Common Issues

1. **No components found in search**
   - Check if registries are available: `python3 v2/core/01-mcp-server/mcp_server.py list-registries`
   - Try broader search terms
   - Verify platform context is set correctly

2. **Component not found**
   - Use exact component name: `button` instead of `"Button Component"`
   - Check available components: `python3 v2/core/01-mcp-server/mcp_server.py list-components`
   - Try different registry: `--registry gluestack_db`

3. **Registry not available**
   - Check registry status: `python3 v2/core/01-mcp-server/mcp_server.py list-registries`
   - Verify platform compatibility
   - Check if registry is marked as `is_active: true`

### Debug Commands

```bash
# Check available registries
python3 v2/core/01-mcp-server/mcp_server.py list-registries

# Verify current context
python3 v2/core/01-mcp-server/mcp_server.py get-context

# Test basic search
python3 v2/core/01-mcp-server/mcp_server.py search "button" --limit 1

# List component types
python3 v2/core/01-mcp-server/mcp_server.py list-components --type ui --limit 5
```

## Integration Examples

### For AI Assistants

```javascript
// Example: Claude/ChatGPT integration
async function findComponents(requirement, platform = 'reactjs') {
  // Set context
  await exec(`python3 v2/core/01-mcp-server/mcp_server.py set-context ${platform}`);

  // Search for components
  const searchResult = await exec(`python3 v2/core/01-mcp-server/mcp_server.py search "${requirement}" --format json`);
  const searchData = JSON.parse(searchResult.stdout);

  if (searchData.success && searchData.data.total_found > 0) {
    // Get details for top components
    const components = searchData.data.components.slice(0, 3);
    const details = await Promise.all(
      components.map(comp =>
        exec(`python3 v2/core/01-mcp-server/mcp_server.py get-component ${comp.name} --format json`)
      )
    );

    return details.map(d => JSON.parse(d.stdout).data);
  }

  return [];
}
```

### For Development Workflows

```bash
#!/bin/bash
# setup-project-components.sh - Project component setup script

PLATFORM=${1:-reactjs}
SESSION_ID="setup-$(date +%s)"

echo "Setting up components for $PLATFORM project..."

# Set context
python3 v2/core/01-mcp-server/mcp_server.py set-context $PLATFORM --session-id $SESSION_ID

# Find essential components
echo "Finding essential components..."
python3 v2/core/01-mcp-server/mcp_server.py search "button input form dialog card" --limit 20 --format table

echo "Use get-component command to get installation details for specific components."
echo "Example: python3 v2/core/01-mcp-server/mcp_server.py get-component button"
```

## Getting Help

- **Command help**: Use `--help` with any command
- **Available registries**: `python3 v2/core/01-mcp-server/mcp_server.py list-registries`
- **Current context**: `python3 v2/core/01-mcp-server/mcp_server.py get-context`
- **Component exploration**: `python3 v2/core/01-mcp-server/mcp_server.py list-components --limit 10`