# Project Brief: Minimal Shadcn Components MCP RAG

## Executive Summary
Build a minimal, local MCP RAG system specifically for shadcn React components to help AI developers quickly find, understand, and install the right components. This is a personal use MVP - minimal effort, immediate usability, no tests, just the core functionality needed to make it work NOW.

## Problem Statement
I need to quickly find shadcn components while working with AI assistants. Currently, I have to manually search through the shadcn registry or documentation, which breaks my workflow. I want to ask my AI assistant "find me a modal dialog component" and get back the exact component name, install command, and dependencies.

**Key pain point:** Manual component discovery slows down development workflow with AI assistants.

## Proposed Solution
**Minimal MVP Approach:**
- Parse existing shadcn registry files from `/Users/tbardale/github/shadcn-ui/`
- Create simple JSON index with component metadata
- Build MCP server with 4 basic tools for component search
- Use ChromaDB for local vector storage
- No UI, no tests, no complex features - just the core search functionality

**Data Sources:**
- `apps/v4/registry/registry-ui.ts` (47 components)
- `apps/v4/registry/registry-hooks.ts` (1 hook)
- `apps/v4/registry/registry-blocks.ts` (54 blocks)
- Registry documentation files

## Target Users

### Primary User Segment: Me (Personal Use)
- Developer working with shadcn components
- Uses AI assistants for React development
- Wants quick component discovery and installation info
- Values speed over completeness

## Goals & Success Metrics

### Business Objectives
- Get a working MCP RAG server for shadcn components ASAP
- Reduce component discovery time from minutes to seconds
- Enable natural language component search in AI conversations

### Success Criteria
- **Single command start:** `npm run shadcn-rag`
- **Works offline** after initial indexing
- **<100MB memory usage**
- **<1 second response time**
- **Provides installation commands** for all components
- **Focus ONLY on shadcn** - no other frameworks

## MVP Scope (Minimal Viable Product)

### Core Features (Must Have)
- Parse shadcn registry files into JSON index
- Basic vector search with ChromaDB
- MCP server with 4 tools:
  1. `find_shadcn_component` - natural language search
  2. `get_shadcn_component_details` - complete component info
  3. `list_shadcn_components` - list all components by category
  4. `get_component_installation` - install commands and dependencies
- Simple configuration pointing to shadcn registry directory

### Out of Scope for MVP
- Tests (unit, integration, e2e)
- Web UI or dashboard
- User authentication
- Complex error handling
- Logging and monitoring
- Documentation beyond basic README
- Multiple embedding models
- Advanced search features
- Real-time updates
- Docker containerization

### MVP Success Criteria
I can:
1. Run `npm run shadcn-rag` to start the server
2. Ask my AI assistant to "find a modal dialog component"
3. Get back component name, install command, and dependencies
4. Install the component using the provided command

## Technical Considerations

### Technology Stack (Minimal)
- **Runtime:** Node.js + TypeScript
- **Vector DB:** ChromaDB (local, lightweight)
- **MCP:** Model Context Protocol SDK
- **Search:** Basic semantic search
- **Data:** Parsed from existing registry files

### Architecture
- Single process, no microservices
- In-memory or simple file-based storage
- Direct file system access to shadcn registry
- No external APIs or services

## Constraints & Assumptions

### Constraints
- **Zero budget:** Personal project
- **Immediate need:** Want working solution ASAP
- **Single user:** Just for me
- **Limited scope:** Only shadcn components

### Key Assumptions
- shadcn registry files exist at `/Users/tbardale/github/shadcn-ui/`
- Basic Node.js/TypeScript knowledge
- No need for enterprise features
- Rebuilding from scratch is acceptable if needed

## Risks & Open Questions

### Key Risks
- Registry file format changes could break parsing
- MCP protocol complexity might be underestimated
- ChromaDB setup could be more complex than expected

### Open Questions
- What's the minimal viable embedding model?
- How to handle registry file parsing robustly?
- What's the simplest way to expose MCP tools?

## Next Steps

### Immediate Actions
1. Create focused PRD for this minimal shadcn MCP RAG
2. Prototype registry file parsing
3. Set up basic MCP server structure
4. Implement simple vector search
5. Test with actual AI assistant integration

### PM Handoff
This is a minimal, focused project brief for personal use. Create a PRD that emphasizes speed and simplicity over completeness. Focus only on the 4 core MCP tools and basic functionality needed to make it work immediately.