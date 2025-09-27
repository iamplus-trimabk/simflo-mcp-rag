#!/bin/bash

# SimFlo MCP RAG - Quick Start Script
# This script helps you start the complete system quickly

set -e

echo "🚀 Starting SimFlo MCP RAG System"
echo "=================================="

# Check if we're in the right directory
if [ ! -f "parse_registry.py" ]; then
    echo "❌ Error: Please run this script from the simflo-mcp-rag directory"
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command_exists python3; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

if ! command_exists node; then
    echo "❌ Node.js is required but not installed"
    exit 1
fi

if ! command_exists npm; then
    echo "❌ npm is required but not installed"
    exit 1
fi

echo "✅ Prerequisites found"

# Check if vector database exists
if [ ! -d "chroma_db" ]; then
    echo "📊 Vector database not found. Initializing..."

    # Check if components.json exists
    if [ ! -f "components.json" ]; then
        echo "📄 Components file not found. Parsing registry..."
        python3 parse_registry.py
    fi

    # Create vector database
    python3 vector_store.py --stats
else
    echo "✅ Vector database exists"
fi

# Check if MCP server is built
if [ ! -d "mcp-server/dist" ]; then
    echo "🔨 Building MCP server..."
    cd mcp-server
    npm install
    npm run build
    cd ..
else
    echo "✅ MCP server is built"
fi

# Check if API server is already running
if lsof -i :8000 >/dev/null 2>&1; then
    echo "✅ API server is already running on port 8000"
else
    echo "🌐 Starting API server..."
    python3 api_server.py &
    API_PID=$!

    # Wait for server to start
    sleep 3

    # Check if server started successfully
    if curl -s http://127.0.0.1:8000/health >/dev/null 2>&1; then
        echo "✅ API server started successfully (PID: $API_PID)"
    else
        echo "❌ Failed to start API server"
        exit 1
    fi
fi

# Show system status
echo ""
echo "📊 System Status:"
echo "==============="

# Show database stats
echo "🗄️  Database Information:"
python3 rag_cli.py stats 2>/dev/null | head -10

echo ""
echo "🧪 Testing System:"
echo "=================="

# Test API endpoint
HEALTH_RESPONSE=$(curl -s http://127.0.0.1:8000/health 2>/dev/null || echo '{"status":"error"}')
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo "✅ API health check passed"

    # Test search
    SEARCH_RESPONSE=$(curl -s "http://127.0.0.1:8000/api/v1/components/search?q=button&limit=1" 2>/dev/null || echo '{"success":false}')
    if echo "$SEARCH_RESPONSE" | grep -q "true"; then
        echo "✅ Component search working"
    else
        echo "⚠️  Component search may have issues"
    fi
else
    echo "❌ API health check failed"
fi

echo ""
echo "🎯 Ready to Use!"
echo "==============="
echo ""
echo "1. Python API server is running on http://127.0.0.1:8000"
echo "2. MCP server is built and ready"
echo "3. Vector database contains shadcn components"
echo ""
echo "📖 Next Steps:"
echo "============="
echo "1. Configure your AI assistant to use the MCP server:"
echo "   Path: $(pwd)/mcp-server/dist/index.js"
echo ""
echo "2. Use natural language queries like:"
echo "   - 'Find me modal dialog components'"
echo "   - 'Show me details about the button component'"
echo "   - 'List all UI components'"
echo ""
echo "3. For testing, use the CLI:"
echo "   python3 rag_cli.py interactive"
echo ""
echo "🛑 To stop the server:"
echo "   pkill -f 'python3 api_server.py'"
echo ""
echo "📚 Documentation: See SETUP.md for detailed instructions"