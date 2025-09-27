# Epic 3: Multi-Registry Architecture

## Why This Epic?

Single database search mixes everything together and creates noise. Multiple databases let us keep component libraries separate and search only what's relevant. This makes the system faster, cleaner, and more scalable for adding more libraries in the future.

## What We Need to Build

### Multiple RAG Database Structure
**Goal**: Separate vector databases for each component library

**What to do:**
- Create `rag_databases/` directory structure:
  - `rag_databases/shadcn_db/` (move existing chroma_db here)
  - `rag_databases/gluestack_db/` (new for Gluestack components)
  - Each database has its own ChromaDB instance and components.json
- Update database creation scripts to support multiple registries
- Implement database isolation (no cross-contamination)

**Why separate databases:**
- Search only relevant components (React Native → Gluestack, React JS → Shadcn)
- Faster search performance on smaller datasets
- Easier to add new libraries (just create new database)
- Independent updates and maintenance per library
- Cleaner, more relevant search results

### Registry Manager System
**Goal**: Central system to manage multiple databases and routing

**What to do:**
- Create `registry_manager.py` that handles:
  - Loading available registries from configuration
  - Managing multiple ChromaDB connections
  - Routing searches to correct databases based on context
  - Adding/removing registries dynamically
  - Providing registry statistics and health checks

**Why a registry manager:**
- Single point of control for all databases
- Consistent behavior across registries
- Easy to add new libraries without changing core logic
- Handles complex routing decisions transparently

### Context-Aware Search Routing
**Goal**: Use platform context to decide which databases to search

**What to do:**
- Implement routing logic in registry manager:
  - React Native context → search only gluestack_db
  - React JS context → search only shadcn_db
  - No context → search all or ask user to choose
  - Support for multiple registries per context (future)
- Make routing configurable and extensible
- Add fallback mechanisms when preferred registry has no results

**Why context-aware routing:**
- Eliminates irrelevant results from other platforms
- Dramatically improves search relevance
- Reduces noise in AI assistant responses
- Makes the system feel smarter and more aware

### Database Migration and Setup
**Goal**: Move existing data to new structure and setup new databases

**What to do:**
- Migration script to move `chroma_db/` to `rag_databases/shadcn_db/`
- Update all references to use new database paths
- Create initialization scripts for new Gluestack database
- Setup registry configuration file to track available databases
- Update CLI and API to work with new structure

**Why migration is needed:**
- Can't break existing Shadcn functionality
- Need clean separation from day one
- Existing users need smooth upgrade path
- Configuration-driven approach makes future additions easier

## Where to Implement

### Core Files to Create:
- `registry_manager.py` - Main registry management system
- `rag_databases/registry_config.json` - Configuration for available registries
- `scripts/migrate_databases.py` - Migration script for existing data
- `scripts/initialize_gluestack_db.py` - Setup new Gluestack database

### Files to Modify:
- `vector_store.py` - Update to work with registry manager
- `api_server.py` - Use registry manager instead of direct database access
- `mcp-server/src/index.ts` - Update MCP tools to use registry routing
- `rag_cli.py` - Add registry management commands
- `parse_registry.py` - Support multiple database output

## Success Looks Like

- System maintains separate Shadcn and Gluestack databases
- React Native searches return only Gluestack components
- React JS searches return only Shadcn components
- Easy to add new component libraries (create new database, update config)
- Existing functionality continues to work without changes
- Search results are cleaner and more relevant

## Next Connection

This epic ties everything together. It takes the components extracted by the GitHub Extractor epic, applies the context from the Context Manager epic, and delivers a fast, clean, multi-registry search experience. This is the foundation that makes the whole MVP 2 vision work.