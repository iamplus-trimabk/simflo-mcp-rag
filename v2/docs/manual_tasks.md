# SimFlo RAG - Manual Testing Tasks

## Purpose
Comprehensive guide for manually testing SimFlo RAG functionality in a new Claude Code instance. This document provides setup instructions, configuration, and detailed prompts for testing various SimFlo RAG capabilities.

---

## 1. **Setup: Start SimFlo RAG and mc.json Configuration**

### **Initial Setup Commands:**
```bash
# Navigate to SimFlo RAG directory
cd /Users/tbardale/v2/simflo-mcp-rag

# Commands are auto-loaded in ~/.zshrc, but if needed:
source v2/commands.sh

# Test system is working
simflo_status

# Check available registries
python3 v2/core/01-mcp-server/mcp_server.py list-registries --format json

# Get SimFlo RAG architecture documentation
python3 v2/core/01-mcp-server/mcp_server.py get-component simflo-rag-complete-architecture --registry simflo-rag --format json
```

### **Claude Code mc.json Configuration:**
```json
{
  "mcpServers": {
    "simflo-rag": {
      "command": "python3",
      "args": [
        "/Users/tbardale/v2/simflo-mcp-rag/v2/core/01-mcp-server/mcp_server.py"
      ],
      "cwd": "/Users/tbardale/v2/simflo-mcp-rag"
    }
  }
}
```

### **Quick Verification Commands:**
```bash
# Test SimFlo RAG is working
sm_registries

# Test getting SimFlo RAG documentation
sm_guide

# Test searching gluestack components
sm_search "button component" --limit 3

# Test SimFlo RAG self-documenting system
sm_learn
```

---

## 2. **Task: Build RAG Registry from GitHub Repository**

### **Prompt for GitHub Repository Registry Creation:**
```
I need you to use SimFlo RAG to build a new RAG registry for a GitHub repository.

**Repository Details:**
- Registry Name: [YOUR_REGISTRY_NAME]
- GitHub Repository: [GITHUB_REPO_URL]

**Steps to follow:**
1. Use SimFlo RAG commands to discover content from the GitHub repository
2. Fetch the content using SimFlo RAG content collection
3. Extract structured content using SimFlo RAG extractors
4. Create and build a new registry with the extracted content
5. Verify the registry is working by searching for components

**Available SimFlo RAG Commands:**
- `content_discover --query "[search_terms]" --source-type github --limit 10`
- `content_fetch --source "[GITHUB_REPO_URL]" --output-dir content/`
- `extractors_run_all --parallel --output-dir extracted/`
- `rag_registry_create --name [YOUR_REGISTRY_NAME] --type component --source-dir extracted/`
- `rag_registry_rebuild --registry [YOUR_REGISTRY_NAME]`
- `sm_search "[search_terms]" --limit 5`

**Example Workflow:**
```bash
# Example: Create registry for "react-native-elements"
# Registry Name: react-native-elements
# GitHub Repository: https://github.com/react-native-elements/react-native-elements

content_discover --query "React Native UI components" --source-type github --limit 10
content_fetch --source "https://github.com/react-native-elements/react-native-elements" --output-dir content/react-native-elements/
extractors_run_all --parallel --output-dir extracted/react-native-elements/
rag_registry_create --name react-native-elements --type component --source-dir extracted/react-native-elements/
rag_registry_rebuild --registry react-native-elements
sm_search "button component" --limit 5
```

Please execute these steps and show me the results at each stage.
```

---

## 3. **Task: Build RAG Registry from PDF Document**

### **Prompt for PDF Document Registry Creation:**
```
I need you to use SimFlo RAG to build a RAG registry from a PDF document.

**Document Details:**
- Registry Name: [YOUR_REGISTRY_NAME]
- PDF Document: [PATH_TO_PDF_FILE]

**Steps to follow:**
1. Create a new registry directory structure for the PDF content
2. Extract text content from the PDF using SimFlo RAG extractors
3. Process the extracted text into structured components
4. Create and build a new registry with the processed content
5. Verify the registry is working by searching for topics

**Available SimFlo RAG Commands:**
- `mkdir -p v2/core/00-rag-registry/registries/[YOUR_REGISTRY_NAME]/files/{documentation,guides,reference}`
- `extractors_run pdf-extractor --source-type local --source-path [PATH_TO_PDF_FILE] --output-dir extracted/`
- `rag_registry_create --name [YOUR_REGISTRY_NAME] --type documentation --source-dir extracted/`
- `rag_registry_rebuild --registry [YOUR_REGISTRY_NAME]`
- `sm_search "[topic_from_pdf]" --limit 5`

**Example Workflow:**
```bash
# Example: Create registry from a technical manual PDF
# Registry Name: technical-manual
# PDF Document: /path/to/technical-manual.pdf

mkdir -p v2/core/00-rag-registry/registries/technical-manual/files/{documentation,guides,reference}
extractors_run pdf-extractor --source-type local --source-path "/path/to/technical-manual.pdf" --output-dir extracted/technical-manual/
rag_registry_create --name technical-manual --type documentation --source-dir extracted/technical-manual/
rag_registry_rebuild --registry technical-manual
sm_search "installation guide" --limit 5
```

Please execute these steps and show me the results at each stage.
```

---

## 4. **Task: Convert shadcn Codebase to gluestack using SimFlo RAG**

### **Prompt for Component Library Migration:**
```
I have a React Native app built with shadcn components and I want to convert it to use gluestack components using SimFlo RAG.

**Current Situation:**
- Existing codebase uses shadcn components
- Need to convert to gluestack for React Native compatibility
- Want to use SimFlo RAG to find equivalent gluestack components

**Steps to follow:**
1. Use SimFlo RAG to search for gluestack components equivalent to my current shadcn components
2. Get detailed information about gluestack component usage and API
3. Ask SimFlo RAG for migration patterns and differences
4. Show me how to convert specific components from shadcn to gluestack

**Available SimFlo RAG Commands:**
- `sm_set_context reactnative --session-id conversion-session`
- `sm_search "[shadcn_component_name] equivalent" --limit 3`
- `sm_get "[gluestack_component_name]" --registry gluestack`
- `sm_search "React Native [component_type]" --limit 5`
- `sm_list --type ui --platform reactnative --limit 20`

**Example Component Conversions:**
- Search for: "button component equivalent"
- Search for: "card component React Native"
- Search for: "navigation menu mobile"
- Search for: "form input React Native"

**Migration Workflow Example:**
```bash
# Set React Native context
sm_set_context reactnative --session-id conversion-session

# Find equivalent components
sm_search "button component" --limit 3
sm_get "gluestack-button" --registry gluestack

# Search for React Native specific components
sm_search "card component React Native" --limit 5

# List all React Native compatible components
sm_list --type ui --platform reactnative --limit 20
```

**Specific Conversion Examples:**
- shadcn Button → gluestack Button
- shadcn Card → gluestack Card
- shadcn Input → gluestack Input
- shadcn Dialog → gluestack AlertDialog/Modal
- shadcn Navigation Menu → gluestack Menu/Hamburger

Please start by showing me what gluestack components are available for React Native, then help me convert specific shadcn components from my codebase.
```

---

## 5. **Quick Test Commands for New Claude Code Instance**

### **Immediate Verification Tests:**
```bash
# 1. Test SimFlo RAG Self-Documentation
sm_learn

# 2. Test AI Assistant Guide
sm_guide

# 3. Test Command Reference
sm_commands

# 4. Test Registry Listing
sm_registries

# 5. Test Search Functionality
sm_search "button component" --limit 3

# 6. Test Context Setting
sm_set_context reactnative --session-id test-session

# 7. Test Getting Specific Documents
sm_get "ai-assistant-complete-guide" --registry simflo-rag
```

---

## 6. **Expected Outcomes and Verification**

### **Successful Setup Indicators:**
✅ **SimFlo RAG registry listed** with 15 documentation files
✅ **sm_ commands auto-load** in new shell sessions
✅ **JSON responses** from all MCP server commands
✅ **Component search** returns relevant results
✅ **Context setting** works for platform-specific recommendations

### **Common Troubleshooting:**
- **Command not found**: Commands auto-load via ~/.zshrc, or run `source v2/commands.sh`
- **Registry not found**: Check registry name with `sm_registries` command
- **Empty search results**: Try broader search terms or check registry content
- **Context issues**: Use `sm_set_context` with supported platforms (reactjs, reactnative, auto, none)
- **Help commands**: Use `simflo_help` for all commands, `sm_ai_help` for AI assistant guide

---

## 7. **Advanced Testing Scenarios**

### **Multi-Registry Search:**
```bash
# Search across all registries
sm_search "form validation" --limit 10

# Compare components between registries
sm_search "date picker" --registry shadcn --limit 3
sm_search "date picker" --registry gluestack --limit 3
```

### **Context-Aware Search:**
```bash
# Set React context and search
sm_set_context reactjs --session-id web-app
sm_search "navigation menu" --limit 5

# Set React Native context and search
sm_set_context reactnative --session-id mobile-app
sm_search "navigation menu" --limit 5
```

---

**This document provides comprehensive testing scenarios for validating SimFlo RAG's self-documenting capabilities, registry management, and AI assistant integration features.**