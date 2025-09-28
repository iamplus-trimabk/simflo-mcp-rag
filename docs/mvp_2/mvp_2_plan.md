# MVP 2: Gluestack Integration + Context Awareness

## Vision Enhancement

Extend from **single-library component search** to **multi-library RAG system** with GitHub-based ingestion and basic platform context awareness.

## Phase 1: GitHub Data Extractor

### Story 1.1: Universal GitHub Extractor
**Goal**: Create reusable GitHub repository processor

**Core Functionality:**
- Clone GitHub repositories programmatically
- Parse repository structure for components
- Extract metadata from package.json, README, docs
- Support multiple component library patterns
- Handle both React Native and React JS codebases

**Implementation Plan:**
1. Create `GitHubExtractor` class
2. Implement repository cloning and analysis
3. Build component detection patterns
4. Extract dependencies and metadata
5. Generate structured component data

### Story 1.2: Gluestack Integration
**Goal**: Apply GitHub extractor to Gluestack libraries

**Gluestack Processing:**
- Clone `gluestack/gluestack-ui` repository
- Extract React Native components
- Extract React JS (web) components
- Parse documentation and examples
- Create platform-specific component mappings
- Generate `registry_gluestack.json`

## Phase 2: Context Management System ✅ **COMPLETED**

### Story 2.1: Platform Context Implementation ✅ **COMPLETED**
**Goal**: Add basic platform context awareness

**✅ Completed Implementation:**
- Created `PlatformContext` enum (reactnative | reactjs | auto | none)
- Added comprehensive context management MCP tools
- Modified search to respect platform context with intelligent routing
- Enhanced component indexing with platform tags and registry awareness

**✅ Features Delivered:**
- Thread-safe context management with session tracking
- Platform context validation and error handling
- Context history and session persistence
- Configurable registry mappings via JSON

### Story 2.2: Context-Aware Search ✅ **COMPLETED**
**Goal**: Enhance search with platform filtering

**✅ Completed Features:**
- Platform-specific component recommendations with intelligent routing
- Filter results by current platform context automatically
- Cross-platform component compatibility indicators
- Contextual relevance scoring and ranking algorithms
- Fallback support when context-specific components unavailable

## Phase 3: Multi-Registry Architecture ✅ **COMPLETED**

### Story 3.1: Multiple RAG Database System ✅ **COMPLETED**
**Goal**: Create separate vector databases for each component library

**✅ Completed Implementation:**
- Separate ChromaDB instances: `rag_databases/shadcn_db/`, `rag_databases/gluestack_db/`, `rag_databases/radix_db/`
- Comprehensive Registry Manager to handle multiple databases
- Context-aware registry selection logic with priority-based routing
- Registry index to track available libraries with health monitoring

**✅ Working Results:**
- Gluestack database: 13 components successfully extracted and indexed
- Shadcn database: 102 components with platform-aware routing
- Radix UI database: Ready for component ingestion
- Automatic registry discovery and initialization

### Story 3.2: Context-Aware Search Routing ✅ **COMPLETED**
**Goal**: Route searches to appropriate databases based on context

**✅ Completed Smart Selection Logic:**
- React Native context → priority search Gluestack database, fallback to others
- React JS context → priority search Shadcn database, fallback to others
- Configurable registry mapping per context with JSON configuration
- Intelligent fallback options when no clear context match
- Registry priority scoring and relevance ranking

### Story 3.3: Enhanced MCP Interface ✅ **COMPLETED**
**Goal**: Extend MCP tools for context and registry management

**✅ Implemented MCP Tools (7 Total):**
- `set_platform_context` - Switch between React Native/React JS/Auto/None
- `list_registries` - Show available component libraries with platform filtering
- Enhanced existing tools: `search_components`, `get_component_details`, `get_component_installation`, `list_components` with context awareness

## Technical Implementation

### New System Architecture:
```
Enhanced RAG System
├── GitHub Extractor
│   ├── Repository Cloner
│   ├── Component Parser
│   └── Metadata Extractor
├── Multi-Database System
│   ├── shadcn_db/ (ChromaDB)
│   ├── gluestack_db/ (ChromaDB)
│   └── Registry Manager
├── Context Manager
│   ├── Platform Context (reactnative/reactjs)
│   └── Context-Aware Registry Selection
└── Enhanced MCP Interface
    ├── Context Management Tools
    └── Registry-Aware Search
```

### Key Files to Create/Modify:
- `github_extractor.py` - New GitHub repository processor
- `context_manager.py` - Platform context management
- `registry_manager.py` - Multiple database handler
- `rag_databases/shadcn_db/` - Existing Shadcn database (move from chroma_db)
- `rag_databases/gluestack_db/` - New Gluestack database
- Enhanced MCP server with context tools
- Updated API server with registry routing

## Success Metrics

### For MVP 2:
- ✅ Successfully extract Gluestack components from GitHub
- ✅ Support both React Native and React JS contexts
- ✅ Demonstrate context-aware component recommendations
- ✅ Search across both Shadcn and Gluestack registries
- ✅ Seamless platform switching via MCP tools

## Implementation Strategy

### Week 1: GitHub Extractor
- Build universal GitHub extraction framework
- Implement Gluestack repository processing
- Create structured component data export

### Week 2: Context System
- Implement platform context management
- Add context-aware search capabilities
- Update MCP tools for context switching

### Week 3: Integration & Testing
- Integrate both registries into unified system
- Test context-aware recommendations
- Polish user experience and documentation

## Future Expansion

See `docs/future/future_plan.md` for the comprehensive vision beyond MVP 2, including:
- Multi-source data extractors (web, APIs, documentation)
- Rich context dimensions (backend, testing, deployment)
- Advanced knowledge intelligence and relationship mapping
- Predictive assistance and collaborative features

This focused MVP delivers tangible value by adding Gluestack support and basic context awareness while keeping the scope manageable and achievable.