# SimFlo MCP RAG - Complete Setup Guide

This guide will help you set up the complete SimFlo MCP RAG system for searching shadcn components with AI assistants.

## System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   AI Assistant  │◄──►│  MCP Server      │◄──►│  Python RAG     │
│  (Claude/GPT)   │    │  (TypeScript)    │    │  API Server     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ ChromaDB Vector │
                       │    Database     │
                       └─────────────────┘
```

## Prerequisites

### System Requirements
- **Operating System**: macOS, Linux, or Windows (with WSL2)
- **Python**: 3.9 or later
- **Node.js**: 18 or later
- **Memory**: 4GB RAM minimum (8GB recommended)
- **Disk Space**: 500MB for the system + vector database

### Required Files
- Access to shadcn registry files (usually in `/Users/tbardale/github/shadcn-ui/apps/v4/registry/`)

## Quick Start (One-time Setup)

### 1. Clone and Setup Repository

```bash
# Navigate to your development directory
cd /Users/tbardale/v2

# Clone or navigate to the repository
cd simflo-mcp-rag

# Install Python dependencies
pip install -r requirements.txt

# Setup MCP server
cd mcp-server
npm install
npm run build
cd ..
```

### 2. Initialize the RAG Database

```bash
# Parse shadcn registry files (one-time operation)
python3 parse_registry.py

# Index components in vector database (one-time operation)
python3 vector_store.py --stats

# Verify the setup
python3 rag_cli.py stats
```

### 3. Test the System

```bash
# Start the Python API server
python3 api_server.py &

# Test the API endpoints
curl -s http://127.0.0.1:8000/health
curl -s "http://127.0.0.1:8000/api/v1/components/search?q=modal"
```

## Daily Usage

### Starting the System

1. **Start Python API Server:**
```bash
python3 api_server.py --host 127.0.0.1 --port 8000
```

2. **Configure AI Assistant:**
   - Add the MCP server to your AI assistant configuration
   - Server executable: `/Users/tbardale/v2/simflo-mcp-rag/mcp-server/dist/index.js`

### Using with AI Assistants

Once configured, you can use natural language queries:

**Search for components:**
- "Find me modal dialog components"
- "Search for form validation components"
- "Show me calendar date picker components"

**Get component details:**
- "Tell me about the button component"
- "What dependencies does the dialog component need?"
- "How do I install the input component?"

**Browse components:**
- "List all UI components"
- "Show me available block components"
- "What hooks are available?"

## Advanced Usage

### CLI Testing Interface

```bash
# Interactive mode for testing
python3 rag_cli.py interactive

# Search from command line
python3 rag_cli.py search "modal dialog"

# Get component details
python3 rag_cli.py details button

# List components by type
python3 rag_cli.py list --type ui

# Show database statistics
python3 rag_cli.py stats
```

### API Reference

The Python API server provides these endpoints:

- `GET /health` - System health check
- `GET /api/v1/components/search?q=<query>&limit=<n>` - Search components
- `GET /api/v1/components/<name>` - Get component details
- `GET /api/v1/components/<name>/installation` - Get installation info
- `GET /api/v1/components?type=<type>&limit=<n>` - List components
- `GET /api/v1/stats` - Get database statistics

### MCP Tools Reference

The MCP server provides these tools:

- `search_components` - Natural language component search
- `get_component_details` - Detailed component information
- `get_component_installation` - Installation guides and dependencies
- `list_components` - Browse components by type

## Troubleshooting

### Common Issues

**Registry Files Not Found:**
```bash
# Check the registry path
ls /Users/tbardale/github/shadcn-ui/apps/v4/registry/

# Update the path if needed
python3 parse_registry.py --registry-path /path/to/registry
```

**Vector Store Empty:**
```bash
# Re-index components
python3 vector_store.py --stats

# Check components.json exists
ls -la components.json
```

**API Server Won't Start:**
```bash
# Check port 8000 is available
lsof -i :8000

# Try different port
python3 api_server.py --port 8001
```

**MCP Server Issues:**
```bash
# Rebuild the server
cd mcp-server
npm run build
npm run type-check
```

### Performance Tips

- The Python API server uses in-memory caching for fast responses
- Vector search is optimized for natural language queries
- Components are pre-indexed for instant search results

### Database Management

**Update Component Database:**
```bash
# Re-parse registry files
python3 parse_registry.py

# Re-index vector store
python3 vector_store.py --stats
```

**Reset Database:**
```bash
# Remove vector database
rm -rf chroma_db

# Remove components cache
rm -f components.json

# Rebuild from scratch
python3 parse_registry.py
python3 vector_store.py --stats
```

## Configuration

### Environment Variables

```bash
# Python API Server (optional)
export API_HOST=127.0.0.1
export API_PORT=8000

# MCP Server (optional)
export API_BASE_URL=http://127.0.0.1:8000
```

### Custom Registry Path

```bash
# Use custom shadcn registry path
python3 parse_registry.py --registry-path /custom/path/to/registry
```

## Integration Examples

### Claude Desktop Configuration

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "simflo-rag": {
      "command": "node",
      "args": ["/Users/tbardale/v2/simflo-mcp-rag/mcp-server/dist/index.js"],
      "env": {
        "API_BASE_URL": "http://127.0.0.1:8000"
      }
    }
  }
}
```

### VS Code Integration

Use the MCP server with VS Code's AI extensions by configuring it in your settings.

## System Status Verification

Run these commands to verify everything is working:

```bash
# 1. Check Python RAG database
python3 rag_cli.py stats

# 2. Test API server
curl -s http://127.0.0.1:8000/health | jq .

# 3. Test search functionality
curl -s "http://127.0.0.1:8000/api/v1/components/search?q=button&limit=3" | jq .

# 4. Verify MCP server build
cd mcp-server && npm run type-check && cd ..
```

Expected output should show:
- 102 total components (47 UI, 54 blocks, 1 hook)
- API server responding with health status
- Search returning relevant results
- MCP server building without errors

## Support

If you encounter issues:
1. Check this troubleshooting section
2. Verify all prerequisites are installed
3. Ensure the Python API server is running
4. Check file permissions and paths
5. Review the individual component documentation

The system is designed to be minimal and straightforward - most issues relate to file paths or missing dependencies.