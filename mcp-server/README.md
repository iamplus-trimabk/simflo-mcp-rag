# SimFlo MCP RAG Server

MCP (Model Context Protocol) server that enables AI assistants to search and retrieve information about shadcn/ui components using natural language queries.

## Features

- **Natural Language Search**: Search for components using everyday language
- **Component Details**: Get detailed information about specific components
- **Installation Guides**: Get installation commands and setup notes
- **Component Discovery**: Browse available components by type
- **Smart Integration**: Seamlessly integrates with AI assistants

## Available Tools

### `search_components`
Search for shadcn components using natural language queries.

**Parameters:**
- `query` (required): Natural language search query (e.g., "modal dialog", "form input validation")
- `limit` (optional): Maximum number of results (1-50, default: 10)

**Example:**
```
Search for modal dialog components with good accessibility
```

### `get_component_details`
Get detailed information about a specific component.

**Parameters:**
- `name` (required): Component name (e.g., "button", "dialog", "input")

### `get_component_installation`
Get installation information and setup notes for a component.

**Parameters:**
- `name` (required): Component name (e.g., "button", "dialog", "input")

### `list_components`
List available components, optionally filtered by type.

**Parameters:**
- `type` (optional): Filter by component type ("ui", "block", "hook")
- `limit` (optional): Maximum number of results (1-100, default: 20)

## Setup

### Prerequisites

1. Python RAG server running on `http://127.0.0.1:8000`
2. Node.js 18+ installed

### Installation

1. Build the server:
```bash
npm run build
```

2. Configure with your AI assistant (Claude, ChatGPT, etc.) using the MCP protocol.

### Configuration

The server connects to the Python RAG API server. You can configure the API URL:

```bash
export API_BASE_URL=http://127.0.0.1:8000
```

## Development

```bash
# Install dependencies
npm install

# Run in development mode
npm run dev

# Build for production
npm run build

# Run type checking
npm run type-check

# Run linting
npm run lint
```

## Testing the Server

Start the Python API server first:
```bash
cd /Users/tbardale/v2/simflo-mcp-rag
python3 api_server.py
```

Then test the MCP server functionality through your AI assistant.

## Example Usage

Once configured with your AI assistant, you can use natural language queries like:

- "Find me a calendar date picker component"
- "Show me details about the button component"
- "What do I need to install the dialog component?"
- "List all available block components"

The server will provide detailed information about shadcn components including installation commands, dependencies, and usage guidance.