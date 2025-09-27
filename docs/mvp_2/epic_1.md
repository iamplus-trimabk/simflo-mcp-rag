# Epic 1: GitHub Data Extractor

## Why This Epic?

Currently, the system only processes local registry files. To expand to other component libraries like Gluestack, we need a way to extract component information from GitHub repositories. This creates a reusable pipeline that can work with any GitHub-hosted component library.

## What We Need to Build

### GitHub Repository Extractor
**Goal**: Clone and process GitHub repositories to extract component information

**What to do:**
- Create `github_extractor.py` that can:
  - Clone any GitHub repository given a URL
  - Scan the repository structure for component files
  - Extract component metadata from package.json, README files, and source code
  - Parse component definitions from TypeScript/JavaScript files
  - Generate structured component data similar to our current registry format

**Why this approach:**
- One extractor can work with any component library
- No manual parsing required for each new library
- Automatically stays updated with library changes
- Captures real examples and documentation from the source

### Gluestack Processing Pipeline
**Goal**: Apply the GitHub extractor specifically to Gluestack libraries

**What to do:**
- Configure extractor to work with `gluestack/gluestack-ui` repository
- Handle both React Native and React JS component variations
- Parse Gluestack's specific component structure and documentation
- Generate `rag_databases/gluestack_db/components.json` with structured data
- Create separate indexes for React Native vs React JS components

**Why Gluestack first:**
- Popular library with good documentation
- Supports both React Native and React JS
- Demonstrates the power of context-aware search
- Real-world use case for the extractor

### Repository Structure Understanding
**Goal**: Make the extractor smart about different repository layouts

**What to do:**
- Detect common component library patterns:
  - `components/` directories
  - `ui/` or `src/components/` structures
  - Export files with component definitions
  - Documentation files with usage examples
- Handle different file naming conventions
- Extract dependencies and import statements
- Capture component props and usage patterns

**Why this matters:**
- Different libraries organize code differently
- Need flexibility to handle various layouts
- Captures the full component ecosystem, not just basic info

## Where to Implement

### Core Files to Create:
- `github_extractor.py` - Main extraction logic
- `tests/test_github_extractor.py` - Verify extraction works
- `scripts/extract_gluestack.py` - Script to run Gluestack extraction

### Integration Points:
- Modify `vector_store.py` to support multiple databases
- Update API endpoints to handle registry selection
- Extend MCP tools to work with new registries

## Success Looks Like

- Running `python github_extractor.py https://github.com/gluestack/gluestack-ui` generates a complete component database
- Extracted data includes component names, descriptions, dependencies, examples, and platform compatibility
- System can distinguish between React Native and React JS components
- Extractor works with minimal configuration for new repositories

## Next Connection

This epic enables the Context Manager epic by providing the Gluestack component data that needs context-aware routing. Without extracted components, there's nothing to apply context to.