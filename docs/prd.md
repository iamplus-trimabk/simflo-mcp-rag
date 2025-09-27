# Minimal Shadcn Components MCP RAG Product Requirements Document (PRD)

## Goals and Background Context

### Goals
- Enable natural language search of shadcn components through AI assistants using MCP protocol
- Reduce component discovery time from manual search to instant AI-powered queries
- Provide complete installation information including dependencies and commands
- Create a minimal, local-only solution that works offline after initial indexing
- Achieve single-command startup and sub-second response times

### Background Context
This project addresses the workflow friction when developing React applications with shadcn components and AI assistants. Currently, developers must manually search through shadcn documentation or registry files to find components, breaking the conversational flow with AI assistants.

Based on research of the actual shadcn registry at `/Users/tbardale/github/shadcn-ui/`, the system will index 47 UI components, 54 blocks, and 1 hook (`use-mobile`) from the real registry files, not the broader list shown on the shadcn website. This ensures the RAG system provides accurate, actionable information for components that are actually available for installation.

### Change Log
| Date | Version | Description | Author |
|------|---------|-------------|---------|
| 2025-01-28 | 1.0 | Initial PRD creation based on actual registry data | BMAD Orchestrator |

## Requirements

### Functional Requirements

**FR1: Registry Data Parsing**
- Parse shadcn registry files: `registry-ui.ts` (47 components), `registry-blocks.ts` (54 blocks), `registry-hooks.ts` (1 hook)
- Extract component metadata including name, dependencies, registryDependencies, files, and descriptions
- Combine with documentation from `COMPONENTS_REGISTRY.md`, `HOOKS_REGISTRY.md`, and `BLOCKS_REGISTRY.md`
- Generate structured JSON index with all required fields for search and retrieval

**FR2: Vector Search Index**
- Create and maintain vector embeddings for component search using component names, descriptions, and use cases
- Support semantic search capabilities for natural language queries
- Store component metadata alongside vectors for retrieval
- Provide relevance ranking based on semantic similarity

**FR3: MCP Server Implementation**
- Implement MCP protocol server using official MCP SDK for Node.js
- Expose 4 core tools through MCP protocol:
  - `find_shadcn_component` - Natural language component search
  - `get_shadcn_component_details` - Complete component information retrieval
  - `list_shadcn_components` - List all components by category with filtering
  - `get_component_installation` - Installation commands and dependency management
- Handle MCP client connections and tool execution requests

**FR4: Tool Functionality**
- `find_shadcn_component(query: string)`: Return list of relevant components with basic info ranked by relevance
- `get_shadcn_component_details(name: string)`: Return complete component information including dependencies, files, description, usage guidelines
- `list_shadcn_components(category?: string)`: Return all available components with optional filtering by type (ui, hooks, blocks)
- `get_component_installation(name: string)`: Return installation command, all dependencies (npm and registry), and setup notes

**FR5: Configuration Management**
- Simple configuration pointing to shadcn registry directory (`/Users/tbardale/github/shadcn-ui/`)
- Environment variables for server settings (port, log level, etc.)
- Command-line argument support for common options

### Non Functional Requirements

**NFR1: Performance**
- Startup time: < 10 seconds from command to ready state
- Response time: < 1 second for all tool operations
- Memory usage: < 100MB during operation
- Indexing time: < 30 seconds for initial registry processing

**NFR2: Usability**
- Single command startup: `npm run shadcn-rag`
- Works offline after initial indexing
- No complex setup or configuration required
- Clear error messages for common issues

**NFR3: Technical Constraints**
- Local-only operation (no external APIs or services)
- Minimal dependencies (only essential packages)
- No authentication or user management required
- No persistent logging or monitoring

**NFR4: Data Accuracy**
- Parse only actual registry files (not website content)
- Provide real installation commands from registry data
- Include actual dependencies and registry dependencies
- Use real file paths from registry

## User Interface Design Goals

### Overall UX Vision
This is a headless MCP service with no user interface. The UX is defined by the MCP tool interfaces and the AI assistant interaction model. The focus is on providing clean, predictable tool responses that integrate seamlessly with AI assistant conversations.

### Key Interaction Paradigms
- **Conational**: Users interact through natural language conversations with AI assistants
- **Tool-based**: AI assistants use MCP tools to retrieve component information
- **Response-driven**: Each tool returns structured data for the AI to present to users

### Core "Screens" and Views
- **Tool Response Views**: Structured JSON responses from each MCP tool
- **Error Responses**: Clear error messages for invalid requests or missing data
- **Status Indicators**: Basic server status and health check endpoints

### Accessibility: None
This is a headless service with no direct user interface.

### Branding: None
No branding requirements for this personal tool.

### Target Device and Platforms: Local Development Environment
- Node.js runtime environment
- macOS/Linux/Windows development machines
- AI assistants with MCP protocol support (Claude Desktop, etc.)

## Technical Assumptions

### Repository Structure: Monorepo
Single repository containing all service components with clear separation of concerns for maintainability and simplicity.

### Service Architecture: Monolith
Single-process service architecture with modular components:
- Registry parser for extracting component data
- Vector store for semantic search capabilities
- MCP server for protocol handling
- Configuration management for settings

### Testing Requirements: None
Per project brief, this is a minimal MVP with no testing requirements to speed up development.

### Additional Technical Assumptions and Requests
- **Language**: Node.js with TypeScript for type safety and modern JavaScript features
- **Vector Database**: ChromaDB for local, lightweight vector storage and search
- **MCP Protocol**: Official `@modelcontextprotocol/sdk` package for protocol implementation
- **Embeddings**: Built-in embedding support from ChromaDB or minimal embedding library
- **File System**: Direct access to shadcn registry files at `/Users/tbardale/github/shadcn-ui/`
- **Dependencies**: Minimal, well-maintained packages from npm
- **Configuration**: JSON configuration file with environment variable overrides
- **Error Handling**: Basic error handling with informative messages
- **Logging**: Console logging for development, no persistent logging required

## Epic List

### Epic 1: Foundation & Core MCP Server
Establish the project structure, registry parsing, vector search, and MCP server implementation to deliver a working component search service.

### Epic 2: Enhanced Search & Integration
Improve search relevance, add filtering capabilities, and integrate with AI assistant workflows for better user experience.

## Epic Details

### Epic 1 Foundation & Core MCP Server
**Goal**: Implement the complete minimal MVP including registry parsing, vector search, MCP server, and all 4 core tools to deliver a working shadcn component discovery service.

#### Story 1.1 Project Setup & Configuration
As a developer,
I want to set up the project structure and basic configuration,
so that I have a foundation for building the MCP RAG service.

**Acceptance Criteria:**
1. Initialize Node.js project with TypeScript configuration
2. Set up package.json with required dependencies (MCP SDK, ChromaDB, TypeScript)
3. Create basic project structure with source directories
4. Implement simple configuration system pointing to shadcn registry directory
5. Add basic startup script (`npm run shadcn-rag`)
6. Verify project can be started and loads configuration correctly

#### Story 1.2 Registry Data Parser
As a developer,
I want to parse shadcn registry files and extract component metadata,
so that I have structured data for indexing and search.

**Acceptance Criteria:**
1. Parse `registry-ui.ts` and extract all 47 UI components with metadata
2. Parse `registry-blocks.ts` and extract all 54 blocks with dependencies
3. Parse `registry-hooks.ts` and extract `use-mobile` hook information
4. Extract key fields: name, type, dependencies, registryDependencies, files, descriptions
5. Combine with documentation from registry MD files for enhanced descriptions
6. Generate unified JSON index with all component data
7. Handle parsing errors gracefully with informative messages
8. Output parsed data to console for verification

#### Story 1.3 Vector Search Implementation
As a developer,
I want to implement vector search capabilities for component descriptions,
so that users can search for components using natural language.

**Acceptance Criteria:**
1. Set up ChromaDB for local vector storage
2. Create vector embeddings from component names, descriptions, and use cases
3. Store component metadata alongside vectors for retrieval
4. Implement semantic search function with relevance ranking
5. Support basic text matching as fallback for simple queries
6. Test search with sample queries (e.g., "modal dialog", "date picker")
7. Verify search returns relevant results with proper ranking
8. Handle edge cases (empty queries, no results found)

#### Story 1.4 MCP Server Core
As a developer,
I want to implement the MCP server with protocol handling,
so that AI assistants can connect and use the component search tools.

**Acceptance Criteria:**
1. Set up MCP server using official SDK
2. Implement server startup and connection handling
3. Create basic server health check endpoint
4. Handle MCP protocol messages and tool execution
5. Implement proper error handling and response formatting
6. Add graceful shutdown handling
7. Test server can start and accept connections
8. Verify server responds to basic MCP protocol messages

#### Story 1.5 MCP Tools Implementation
As a developer,
I want to implement the 4 core MCP tools for component search,
so that AI assistants can find and retrieve shadcn component information.

**Acceptance Criteria:**
1. Implement `find_shadcn_component(query: string)` tool with natural language search
2. Implement `get_shadcn_component_details(name: string)` tool with complete component info
3. Implement `list_shadcn_components(category?: string)` tool with filtering support
4. Implement `get_component_installation(name: string)` tool with installation commands
5. Each tool returns properly formatted JSON responses
6. Tools handle error cases (invalid names, no results found)
7. Tools use vector search and parsed registry data
8. Test all tools with sample requests and verify responses

#### Story 1.6 End-to-End Integration
As a user,
I want to use the complete MCP RAG service with my AI assistant,
so that I can search for shadcn components naturally in conversations.

**Acceptance Criteria:**
1. Start service with single command (`npm run shadcn-rag`)
2. Connect MCP server to AI assistant (Claude Desktop or similar)
3. Test natural language queries: "find me a modal dialog component"
4. Verify AI assistant can find and present component information
5. Test complete workflow: search → get details → get installation info
6. Verify response times are < 1 second
7. Confirm memory usage stays < 100MB
8. Test with various component types (UI, blocks, hooks)

### Epic 2 Enhanced Search & Integration
**Goal**: Improve search relevance, add filtering capabilities, and enhance integration with AI assistant workflows for better user experience and more accurate component discovery.

#### Story 2.1 Search Relevance Improvements
As a user,
I want more accurate search results with better relevance ranking,
so that I can find the most appropriate components for my needs.

**Acceptance Criteria:**
1. Improve search algorithm with better relevance scoring
2. Add boost factors for component names vs descriptions
3. Implement search result diversity to avoid similar components
4. Add partial text matching for component names
5. Improve handling of multi-word queries and synonyms
6. Test with ambiguous queries and verify best matches
7. Add search result relevance scores in responses
8. Benchmark search accuracy against manual lookup

#### Story 2.2 Advanced Filtering & Categorization
As a user,
I want to filter and browse components by specific criteria,
so that I can narrow down options based on my requirements.

**Acceptance Criteria:**
1. Add filtering by dependency types (Radix UI, date libraries, etc.)
2. Implement component categorization by use case
3. Add filtering by component complexity (simple vs advanced)
4. Support filtering by registry dependencies
5. Add component tags for better classification
6. Implement multiple filter combinations
7. Update `list_shadcn_components` tool with advanced filtering
8. Test filtering with various use cases and verify results

#### Story 2.3 Usage Examples & Integration Patterns
As a user,
I want to see usage examples and integration patterns,
so that I can understand how to use components effectively.

**Acceptance Criteria:**
1. Extract code examples from registry documentation
2. Include common usage patterns in component details
3. Add import statement examples
4. Provide TypeScript usage examples
5. Include dependency installation order information
6. Add common gotchas and troubleshooting tips
7. Update `get_shadcn_component_details` with usage examples
8. Test examples are accurate and helpful

#### Story 2.4 Performance Optimization
As a user,
I want faster response times and lower memory usage,
so that the service is more efficient for personal use.

**Acceptance Criteria:**
1. Optimize vector search performance with better indexing
2. Implement result caching for common queries
3. Reduce memory footprint with efficient data structures
4. Optimize registry parsing for faster startup
5. Add lazy loading for large component datasets
6. Implement connection pooling for better resource usage
7. Benchmark performance improvements
8. Verify service still meets <100MB memory and <1s response requirements

## Checklist Results Report

*Checklist will be executed after PRD review and approval*

## Next Steps

### UX Expert Prompt
*Not applicable for this headless service*

### Architect Prompt
Create a technical architecture for the minimal shadcn MCP RAG service based on this PRD. Focus on:
- Simple, modular component design
- Efficient registry parsing and vector search implementation
- Clean MCP protocol integration
- Performance optimization for personal use
- Minimal dependencies and straightforward implementation

The architecture should enable rapid development while meeting all requirements for single-command startup, sub-second response times, and offline operation.