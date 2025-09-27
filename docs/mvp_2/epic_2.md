# Epic 2: Context Management System

## Why This Epic?

Right now, the system treats all components the same way. But React Native and React JS have different component needs, patterns, and libraries. A developer working on mobile needs different results than someone working on web. Context makes the search smarter and more relevant.

## What We Need to Build

### Platform Context Implementation
**Goal**: Basic awareness of whether the user is working with React Native or React JS

**What to do:**
- Create `context_manager.py` to handle platform context:
  - Support `reactnative` and `reactjs` as platform options
  - Store current context in memory/session
  - Provide simple API to get/set current context
  - Default context can be configured or auto-detected

**Why these two platforms:**
- React Native = mobile development with specific UI needs
- React JS = web development with different component patterns
- Gluestack and Shadcn each excel in different platforms
- Clear separation makes search results more relevant

### Context-Aware Registry Selection
**Goal**: Route searches to the right database based on platform context

**What to do:**
- Create mapping between context and appropriate registries:
  - `reactnative` context → search `gluestack_db` only
  - `reactjs` context → search `shadcn_db` only
- Implement selection logic in registry manager
- Handle cases where context isn't set (show both or ask)
- Make selection configurable per user preference

**Why this routing matters:**
- No noise from irrelevant platforms in results
- Faster search (smaller databases)
- Better relevance scoring
- Cleaner user experience

### MCP Context Tools
**Goal**: Let users control context through AI assistant conversations

**What to do:**
- Add MCP tool `set_platform_context` with options:
  - `reactnative` for mobile development
  - `reactjs` for web development
  - `auto` for intelligent detection (future)
- Update existing search tools to respect current context
- Add context indicators to search results
- Allow users to see current context and available options

**Why MCP tools for context:**
- Natural way to set context through conversation
- No need to switch to different interfaces
- Context persists through the AI session
- Enables "I'm building a mobile app" → automatically use React Native context

### API Context Integration
**Goal**: Make the HTTP API aware of platform context

**What to do:**
- Add context parameter to search endpoints:
  - `/api/v1/components/search?query=button&platform=reactnative`
- Support context in request headers
- Update vector store integration to use context
- Return context information in API responses

**Why API integration:**
- Supports non-MCP clients
- Enables context-aware web interfaces
- Makes the system more flexible
- Future-proofs for additional contexts

## Where to Implement

### Core Files to Create:
- `context_manager.py` - Context handling logic
- `registry_manager.py` - Multiple database management with context routing

### Files to Modify:
- `api_server.py` - Add context endpoints and parameters
- `mcp-server/src/index.ts` - Add context MCP tools
- `vector_store.py` - Support multiple database access
- `rag_cli.py` - Add context commands for testing

## Success Looks Like

- User says "I'm working on a React Native project" → system automatically searches Gluestack
- User says "Switch to React JS" → system starts searching Shadcn
- Search results show only platform-relevant components
- Context persists through the conversation without repetition
- API calls respect platform context and return filtered results

## Next Connection

This epic makes the Multi-Registry Architecture epic useful. Without context, multiple databases are just separate data stores. With context, they become an intelligent, user-aware system that delivers the right components for the right platform.