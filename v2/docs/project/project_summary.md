# Minimal Shadcn Components MCP RAG System

## 🎯 Focused Goal
Build a simple, local RAG system specifically for shadcn React components to help AI developers quickly find, understand, and install the right components.

## 📋 What We'll Index

### Data Sources (Single Source of Truth)
- **Root Path**: `/Users/tbardale/github/shadcn-ui/`
- **`apps/v4/registry/registry-ui.ts`** - All 47 components with metadata
- **`apps/v4/registry/registry-hooks.ts`** - 1 hook with dependencies
- **`apps/v4/registry/registry-blocks.ts`** - All 54 blocks with dependencies
- **`COMPONENTS_REGISTRY.md`** - Detailed usage descriptions and examples
- **`HOOKS_REGISTRY.md`** - Hook documentation
- **`BLOCKS_REGISTRY.md`** - Block documentation

### Key Data Points per Component
1. **Component metadata**: name, type, file location
2. **Dependencies**: npm packages required (extracted from registry)
3. **Registry dependencies**: other shadcn components needed
4. **Installation command**: `npx shadcn add [component]`
5. **Usage description**: what it does, when to use, when not to use
6. **Code examples**: actual implementation and usage patterns

## 🔧 MCP Server Tools

### 1. `find_shadcn_component`
**Input**: Natural language query
**Output**: List of relevant components with basic info
```typescript
find_shadcn_component("I need a modal dialog with backdrop blur")
// Returns: dialog, drawer components with descriptions
```

### 2. `get_shadcn_component_details`
**Input**: Component name
**Output**: Complete component information
```typescript
get_shadcn_component_details("alert-dialog")
// Returns: {
//   name: "alert-dialog",
//   description: "Accessible alert dialog component",
//   dependencies: ["@radix-ui/react-alert-dialog"],
//   registryDependencies: ["button"],
//   installCommand: "npx shadcn add alert-dialog",
//   whenToUse: ["..."],
//   whenNotToUse: ["..."],
//   codeExample: "...",
//   fileLocation: "ui/alert-dialog.tsx"
// }
```

### 3. `list_shadcn_components`
**Input**: Optional filter (ui, hooks, blocks)
**Output**: All available components by category

### 4. `get_component_installation`
**Input**: Component name
**Output**: Installation steps and dependency management
```typescript
get_component_installation("calendar")
// Returns: {
//   command: "npx shadcn add calendar",
//   dependencies: ["react-day-picker@latest", "date-fns"],
//   registryDependencies: ["button"],
//   setupNotes: "Requires date-fns for date utilities"
// }
```

## 🛠️ Implementation Steps

### Step 1: Data Extraction (JSON Generation)
1. Parse `registry-ui.ts` to extract component metadata and dependencies
2. Combine with documentation from `COMPONENTS_REGISTRY.md`
3. Generate structured JSON index with all required fields
4. Add CLI installation commands for each component
5. **Note**: All file paths are relative to `/Users/tbardale/github/shadcn-ui/`

### Step 2: Simple Search & Indexing
1. **Vector Store**: ChromaDB (local, lightweight)
2. **Embedding**: Basic semantic search using component descriptions
3. **Index**: Component names, descriptions, use cases, and tags
4. **Metadata**: Store dependencies, install commands, code examples

### Step 3: MCP Server Setup
1. Create MCP server with 4 core tools
2. Implement component search by description
3. Add detailed component information retrieval
4. Include installation guidance and dependency info

### Step 4: Simple Web Interface (Optional)
1. Search bar for natural language queries
2. Component cards showing key info and install commands
3. Copy-to-clipboard for installation commands
4. Dependency information display

## 📊 Technology Stack (Minimal)

- **Runtime**: Node.js + TypeScript
- **Vector DB**: ChromaDB (persistent, local)
- **MCP**: Model Context Protocol SDK
- **Search**: Semantic + keyword matching
- **Data**: Parsed from existing registry files

## 🚀 Expected Usage

### For AI Assistant:
```
User: "I need a date picker component for my React app"
AI:
1. find_shadcn_component("date picker calendar")
2. get_shadcn_component_details("calendar")
3. get_component_installation("calendar")
4. Response: "Use the calendar component. Install with: npx shadcn add calendar. Dependencies: react-day-picker@latest, date-fns..."
```

### For Developer:
```
Search: "modal dialog overlay"
Result: dialog component
- Install: npx shadcn add dialog
- Dependencies: @radix-ui/react-dialog
- Code example included
- When to use: confirmations, forms, alerts
```

## ✅ Success Criteria

- **Single command to start**: `npm run shadcn-rag`
- **Works offline** after initial indexing
- **Provides installation commands** for all components
- **Lists all dependencies** clearly
- **Returns actual code examples**
- **Focus ONLY on shadcn** - no other frameworks
- **<100MB memory usage**
- **<1 second response time**

This plan focuses solely on making shadcn components easily discoverable with practical installation and usage information.