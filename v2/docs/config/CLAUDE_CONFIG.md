# Claude Desktop MCP Configuration

## Adding SimFlo MCP RAG to Claude Desktop

### Method 1: Using Claude Desktop Settings UI (Recommended)

1. **Open Claude Desktop Settings**
   - Click on Claude Desktop in the menu bar
   - Select "Settings" or press `Cmd+,`

2. **Navigate to MCP Section**
   - Go to the "Developer" tab
   - Find the "MCP Servers" section

3. **Add the SimFlo MCP Server**
   - Click "Add Server"
   - Enter the following configuration:

   ```json
   {
     "simflo-rag": {
       "command": "node",
       "args": ["/Users/tbardale/v2/simflo-mcp-rag/mcp-server/dist/index.js"],
       "env": {
         "API_BASE_URL": "http://127.0.0.1:8000"
       }
     }
   }
   ```

### Method 2: Manual Configuration File

1. **Find Claude Desktop Config Location**
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. **Edit the Configuration File**
   ```bash
   # Open the config file
   open ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

3. **Add the MCP Server Configuration**
   ```json
   {
     "mcpServers": {
       "playwright": {
         "command": "npx",
         "args": ["@playwright/mcp@latest"]
       },
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

### Method 3: Command Line Alternative

If you prefer using the command line like your example:

```bash
# This is NOT the correct format for local servers
# claude mcp add playwright npx @playwright/mcp@latest

# Instead, you need to manually edit the config file or use the UI
```

## Key Differences from npm-based MCP Servers

### npm-based Servers (like Playwright):
```json
{
  "playwright": {
    "command": "npx",
    "args": ["@playwright/mcp@latest"]
  }
}
```

### Local Servers (like SimFlo MCP RAG):
```json
{
  "simflo-rag": {
    "command": "node",
    "args": ["/absolute/path/to/your/server.js"],
    "env": {
      "ENV_VAR": "value"
    }
  }
}
```

## Before Adding to Claude

### 1. Start the Python API Server
```bash
cd /Users/tbardale/v2/simflo-mcp-rag
python3 api_server.py
```

### 2. Verify the MCP Server is Built
```bash
cd /Users/tbardale/v2/simflo-mcp-rag/mcp-server
npm run build
ls -la dist/index.js  # Should exist
```

### 3. Test the System
```bash
# Test API server
curl -s http://127.0.0.1:8000/health

# Run the quick start script
./start.sh
```

## After Configuration

### 1. Restart Claude Desktop
- Quit Claude Desktop completely
- Restart it for the MCP server to load

### 2. Verify Installation
- Start a new chat in Claude
- Try asking: "What shadcn components are available?"
- You should see responses from the MCP server

### 3. Test Natural Language Queries
- "Find me modal dialog components"
- "Show me details about the button component"
- "What do I need to install the dialog component?"

## Troubleshooting

### Claude Doesn't See the MCP Server

1. **Check the configuration path:**
   ```bash
   # Verify the MCP server exists
   ls -la /Users/tbardale/v2/simflo-mcp-rag/mcp-server/dist/index.js
   ```

2. **Check Claude Desktop logs:**
   - Open Console.app
   - Look for Claude Desktop errors

3. **Verify JSON syntax:**
   - Use a JSON validator to check your config file
   - Ensure no trailing commas

### API Server Connection Issues

1. **Ensure Python API server is running:**
   ```bash
   lsof -i :8000
   ```

2. **Check the environment variable:**
   ```bash
   echo $API_BASE_URL
   # Should be: http://127.0.0.1:8000
   ```

### MCP Server Won't Start

1. **Check Node.js version:**
   ```bash
   node --version  # Should be 18+
   ```

2. **Rebuild the server:**
   ```bash
   cd /Users/tbardale/v2/simflo-mcp-rag/mcp-server
   npm run build
   ```

## Example Working Configuration

Here's a complete example of what your `claude_desktop_config.json` should look like:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    },
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

## Quick Verification Commands

```bash
# 1. Check if MCP server is built
ls -la /Users/tbardale/v2/simflo-mcp-rag/mcp-server/dist/index.js

# 2. Check if API server is accessible
curl -s http://127.0.0.1:8000/health

# 3. Check Claude config location
ls -la ~/Library/Application\ Support/Claude/claude_desktop_config.json

# 4. Test MCP server directly
node /Users/tbardale/v2/simflo-mcp-rag/mcp-server/dist/index.js
```