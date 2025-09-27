#!/bin/bash

# Script to add SimFlo MCP RAG to Claude Desktop configuration

echo "🔧 Adding SimFlo MCP RAG to Claude Desktop..."
echo "=============================================="

# Claude Desktop config location
CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
CLAUDE_CONFIG_FILE="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"

# Check if Claude config directory exists
if [ ! -d "$CLAUDE_CONFIG_DIR" ]; then
    echo "❌ Claude Desktop configuration directory not found:"
    echo "   $CLAUDE_CONFIG_DIR"
    echo ""
    echo "Please ensure Claude Desktop is installed and has been run at least once."
    exit 1
fi

# Check if MCP server is built
MCP_SERVER_PATH="$(pwd)/mcp-server/dist/index.js"
if [ ! -f "$MCP_SERVER_PATH" ]; then
    echo "🔨 MCP server not found. Building it now..."
    cd mcp-server
    npm install
    npm run build
    cd ..

    if [ ! -f "$MCP_SERVER_PATH" ]; then
        echo "❌ Failed to build MCP server"
        exit 1
    fi
fi

# Create backup of existing config
if [ -f "$CLAUDE_CONFIG_FILE" ]; then
    cp "$CLAUDE_CONFIG_FILE" "$CLAUDE_CONFIG_FILE.backup.$(date +%s)"
    echo "✅ Backed up existing configuration"
fi

# Read existing config or create new
if [ -f "$CLAUDE_CONFIG_FILE" ]; then
    EXISTING_CONFIG=$(cat "$CLAUDE_CONFIG_FILE")
else
    EXISTING_CONFIG='{"mcpServers": {}}'
fi

# Check if simflo-rag already exists
if echo "$EXISTING_CONFIG" | grep -q '"simflo-rag"'; then
    echo "⚠️  SimFlo MCP RAG is already configured in Claude Desktop"
    echo "   To update, please manually edit:"
    echo "   $CLAUDE_CONFIG_FILE"
    exit 0
fi

# Create new configuration
NEW_CONFIG=$(echo "$EXISTING_CONFIG" | python3 -c "
import json
import sys

data = json.load(sys.stdin)

# Add simflo-rag configuration
if 'mcpServers' not in data:
    data['mcpServers'] = {}

data['mcpServers']['simflo-rag'] = {
    'command': 'node',
    'args': ['$MCP_SERVER_PATH'],
    'env': {
        'API_BASE_URL': 'http://127.0.0.1:8000'
    }
}

print(json.dumps(data, indent=2))
")

# Write new configuration
echo "$NEW_CONFIG" > "$CLAUDE_CONFIG_FILE"

echo "✅ Configuration added successfully!"
echo ""
echo "📋 Configuration Summary:"
echo "========================"
echo "📁 Config File: $CLAUDE_CONFIG_FILE"
echo "🎯 MCP Server: $MCP_SERVER_PATH"
echo "🌐 API URL: http://127.0.0.1:8000"
echo ""
echo "🚀 Next Steps:"
echo "=============="
echo "1. Restart Claude Desktop completely"
echo "2. Start the Python API server:"
echo "   cd $(pwd)"
echo "   python3 api_server.py"
echo "3. Test in Claude with queries like:"
echo "   'Find me modal dialog components'"
echo "   'Show me details about the button component'"
echo ""
echo "🔍 To verify the configuration, you can check:"
echo "   cat '$CLAUDE_CONFIG_FILE'"
echo ""
echo "⚠️  If you encounter issues:"
echo "   - Ensure Python API server is running on port 8000"
echo "   - Restart Claude Desktop after configuration"
echo "   - Check Claude Desktop logs in Console.app"