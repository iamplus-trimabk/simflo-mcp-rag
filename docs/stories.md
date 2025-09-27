# Streamlined Development Stories - SimFlo MCP RAG

## Development Philosophy

This streamlined approach focuses on building a Python RAG database first, then integrating it with a TypeScript MCP server. No intermediate file-based steps - direct path from data source to RAG to MCP.

**Key Principle**: Build the RAG database with CLI testing first, then integrate with MCP server for AI assistant access.

## Epic 1: Python RAG Database Pipeline with CLI Testing

### Story 1.1: Python script to parse shadcn registry files
**As a developer, I want a Python script that can parse shadcn registry files, so that I can extract structured component data for the RAG database.**

**Acceptance Criteria:**
1. ✅ Parse `registry-ui.ts` and extract all 47 UI components
2. ✅ Parse `registry-blocks.ts` and extract all 54 blocks
3. ✅ Parse `registry-hooks.ts` and extract the `use-mobile` hook
4. ✅ Extract key metadata: name, dependencies, registryDependencies, files, descriptions
5. ✅ Parse registry documentation files:
   - `COMPONENTS_REGISTRY.md` for usage descriptions
   - `HOOKS_REGISTRY.md` for hook documentation
   - `BLOCKS_REGISTRY.md` for block details
6. ✅ Generate structured component data with all available information
7. ✅ Handle file reading errors gracefully
8. ✅ Output parsed data in structured format (JSON) for verification

**Implementation Notes:**
- Read registry files from `/Users/tbardale/github/shadcn-ui/apps/v4/registry/`
- Parse TypeScript registry format to extract component arrays
- Combine structured data with documentation information
- Generate installation commands (`npx shadcn add [component]`)
- Include when to use/when not to use guidelines
- Extract code examples from documentation

**Verification:** Run script and verify output contains all 102 components with complete metadata

---

### Story 1.2: Vector database creation with ChromaDB
**As a developer, I want to create a vector database from the parsed registry data, so that I can perform semantic search on component descriptions.**

**Acceptance Criteria:**
1. ✅ Set up ChromaDB for local vector storage
2. ✅ Create vector embeddings for all component descriptions
3. ✅ Store component metadata alongside vectors for retrieval
4. ✅ Implement efficient indexing of all 102 components
5. ✅ Handle database creation and persistence
6. ✅ Support adding/updating components in the database
7. ✅ Verify database contains all expected components
8. ✅ Test basic vector similarity queries

**Implementation Notes:**
- Use ChromaDB with built-in embeddings for simplicity
- Create searchable text from component names, descriptions, and use cases
- Store component metadata (dependencies, files, examples) with vectors
- Implement batch processing for efficient indexing
- Handle database initialization and error cases

**Verification:** Create database and verify it can be queried for similar components

---

### Story 1.3: CLI interface for database testing
**As a developer, I want a CLI interface to test the RAG database, so that I can verify search functionality before integrating with MCP.**

**Acceptance Criteria:**
1. ✅ Create command-line interface for database queries
2. ✅ Implement search functionality with natural language queries
3. ✅ Support exact component name lookup
4. ✅ Display formatted search results with relevance scores
5. ✅ Show detailed component information on demand
6. ✅ Handle various query types (semantic, exact name, category)
7. ✅ Provide test commands for common use cases
8. ✅ Include help text and usage examples

**Implementation Notes:**
- Use argparse or click for CLI interface
- Implement multiple query modes (search, get-details, list)
- Format output for readability (tables, structured text)
- Include sample queries for testing
- Add error handling for invalid queries or missing components

**Verification:** Test CLI with various queries like "modal dialog", "button", "form input"

---

### Story 1.4: Database query interface
**As a developer, I want a clean query interface for the RAG database, so that the TypeScript MCP server can easily integrate with it.**

**Acceptance Criteria:**
1. ✅ Create Python API for database queries
2. ✅ Implement functions for each MCP tool operation:
   - `find_components(query: str)` for semantic search
   - `get_component_details(name: str)` for full component info
   - `list_components(category: str)` for filtered listings
   - `get_installation_info(name: str)` for setup commands
3. ✅ Handle API errors gracefully with proper error codes
4. ✅ Serialize responses in JSON format for TypeScript consumption
5. ✅ Document the API interface for MCP integration
6. ✅ Test API functions with sample requests
7. ✅ Verify response formats match MCP tool requirements

**Implementation Notes:**
- Create simple REST API or function-based interface
- Use JSON serialization for TypeScript compatibility
- Implement proper error handling and status codes
- Document API endpoints/function signatures
- Add request/response validation
- Test with TypeScript-compatible JSON formats

**Verification:** Test API functions and verify responses can be consumed by TypeScript

---

## Epic 2: TypeScript MCP Server Integration

### Story 2.1: Basic MCP server setup
**As a developer, I want a basic MCP server setup with TypeScript, so that I have the foundation for integrating with the Python RAG database.**

**Acceptance Criteria:**
1. ✅ Initialize TypeScript project with MCP SDK
2. ✅ Set up basic MCP server structure
3. ✅ Configure server to start with `npm run shadcn-rag`
4. ✅ Implement basic server startup and connection handling
5. ✅ Add server health check endpoint
6. ✅ Handle basic MCP protocol messages
7. ✅ Test server can start and accept connections
8. ✅ Verify server responds to basic ping/health checks

**Implementation Notes:**
- Use official `@modelcontextprotocol/sdk` for TypeScript
- Set up basic project structure with TypeScript
- Configure package.json with necessary scripts and dependencies
- Implement basic server with minimal functionality
- Add proper error handling and logging

**Verification:** Start server and verify it can be connected to by MCP clients

---

### Story 2.2: MCP tools for RAG database queries
**As a developer, I want MCP tools that query the Python RAG database, so that AI assistants can search for shadcn components using natural language.**

**Acceptance Criteria:**
1. ✅ Implement `find_shadcn_component` tool using Python RAG database
2. ✅ Implement `get_shadcn_component_details` tool for full component info
3. ✅ Implement `list_shadcn_components` tool with filtering support
4. ✅ Implement `get_component_installation` tool for setup commands
5. ✅ Each tool returns properly formatted JSON responses
6. ✅ Tools handle communication with Python RAG API
7. ✅ Test all tools with sample requests
8. ✅ Verify response formats match AI assistant expectations

**Implementation Notes:**
- Create tool implementations that call Python RAG API
- Handle HTTP/communication errors gracefully
- Format responses for AI assistant consumption
- Add proper input validation and error handling
- Test with various component types and queries

**Verification:** Test tools with AI assistant using natural language queries

---

### Story 2.3: Integration with Python RAG database
**As a developer, I want the MCP server to integrate seamlessly with the Python RAG database, so that AI assistants get accurate, real-time component information.**

**Acceptance Criteria:**
1. ✅ MCP server successfully connects to Python RAG API
2. ✅ All MCP tools return data from Python RAG database
3. ✅ Test end-to-end functionality with AI assistant
4. ✅ Verify search results are relevant and accurate
5. ✅ Handle connection errors gracefully with fallbacks
6. ✅ Test all 4 core tools with various queries
7. ✅ Verify response times are acceptable for AI interaction
8. ✅ Confirm complete workflow works as expected

**Implementation Notes:**
- Implement robust connection handling to Python RAG service
- Add retry logic for transient failures
- Implement proper error handling and user-friendly messages
- Test with comprehensive component queries and use cases
- Ensure seamless integration feels native to AI assistant

**Verification:** Test complete workflow with AI assistant from search to installation commands

---

### Story 2.4: Error handling and polish
**As a developer, I want the MCP server to handle errors gracefully and provide polished responses, so that AI assistants have a smooth experience when using the RAG system.**

**Acceptance Criteria:**
1. ✅ Handle missing components gracefully with helpful error messages
2. ✅ Handle RAG database connection errors with fallbacks
3. ✅ Provide clear, formatted error responses for AI assistants
4. ✅ Add proper input validation for all tool requests
5. ✅ Polish response formats for better AI assistant consumption
6. ✅ Add basic logging for debugging purposes
7. ✅ Test error scenarios and edge cases
8. ✅ Verify error handling doesn't break AI assistant workflow

**Implementation Notes:**
- Implement comprehensive error handling for all failure modes
- Create user-friendly error messages that AI assistants can understand
- Add input validation and sanitization
- Format responses consistently for AI assistant consumption
- Add basic logging for troubleshooting
- Test various error scenarios and edge cases

**Verification:** Test error conditions and verify graceful handling that maintains AI assistant workflow

## Testing Strategy

### Python RAG Database Testing
- **Unit Testing**: Test individual parsing and database functions
- **CLI Testing**: Verify command-line interface works correctly
- **API Testing**: Test query interface with various requests
- **Integration Testing**: Test end-to-end RAG functionality

### TypeScript MCP Server Testing
- **MCP Protocol Testing**: Verify MCP server compliance
- **Tool Testing**: Test each MCP tool with various inputs
- **Integration Testing**: Test communication with Python RAG database
- **End-to-End Testing**: Test complete AI assistant workflow

### Success Metrics
- **Python RAG Database**: All 102 components indexed and searchable
- **CLI Interface**: Usable for manual testing and verification
- **MCP Server**: Successfully connects to AI assistants
- **End-to-End Workflow**: AI assistant can find, get details, and install components
- **Response Quality**: Accurate, helpful responses for AI assistant consumption

## Development Workflow

### Phase 1: Python RAG Database
1. **Story 1.1**: Parse shadcn registry files with Python script
2. **Story 1.2**: Create vector database with ChromaDB
3. **Story 1.3**: Build CLI interface for testing
4. **Story 1.4**: Create query interface for MCP integration

### Phase 2: TypeScript MCP Server
1. **Story 2.1**: Set up basic MCP server with TypeScript
2. **Story 2.2**: Implement MCP tools using Python RAG database
3. **Story 2.3**: Integrate MCP server with Python RAG database
4. **Story 2.4**: Add error handling and polish

This streamlined approach ensures you have a working RAG database with CLI verification before building the MCP server, eliminating redundant implementation steps.