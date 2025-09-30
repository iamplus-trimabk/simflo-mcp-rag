# Directory Structure Planning and Recording

**Session Date**: 2025-09-30
**Objective**: Holistic restructuring of simflo-mcp-rag for long-term maintainability
**Current Status**: Code has become unstructured after evolution cycles - need comprehensive organization

## Guiding Principles

1. **No existing files touched** until new structure is finalized
2. **Build new structure under `/v2/` directory**
3. **Holistic planning** before implementation
4. **Future-proof organization** for scalable evolution
5. **Clean separation of concerns** across all components

## Current Components Identified

### 0. RAG Registry
- Central registry for all RAG systems
- Metadata management
- System configuration and orchestration

### 1. MCP Server Core
- Multi-registry access capabilities
- Context management and setting
- Protocol implementation
- Request routing and orchestration

### 2. RAG Builder
- Content processing from markdown/json files
- Knowledge base construction
- Vector database management
- Index building and optimization

### 3. Extractors Ecosystem
- **Code Extractors**:
  - ReactJS components, hooks, contexts, providers
  - Shadcn component library extraction
  - Gluestack component library extraction
  - General code structure analysis
- **Language Extractors**:
  - TypeScript code analysis
  - Python code analysis
  - Multi-language support
- **Claude-Code Extractor**:
  - Code summarization capabilities
  - Code analysis and insights
  - Documentation generation
  - Evolution tracking

### 4. Content Collection System
- **Source Discovery**:
  - Web search integration
  - AI assistant recommendations
  - Manual source management
  - Source validation and ranking
- **Content Fetching**:
  - GitHub integration (gh cli)
  - Web crawling capabilities
  - Document downloading
  - AI assistant content generation

## Questions for Further Discussion

### Missing Components to Consider:
1. **Testing Infrastructure** - How to organize test files and test data?
2. **Configuration Management** - Environment-specific configs, settings management?
3. **Documentation Structure** - API docs, user guides, developer docs?
4. **Build and Deployment** - CI/CD pipelines, build scripts, deployment configs?
5. **Data Management** - Database schemas, migrations, data validation?
6. **Monitoring and Logging** - System health, performance metrics, error tracking?
7. **Security and Auth** - Authentication, authorization, data protection?
8. **Utilities and Helpers** - Common functions, shared utilities?
9. **Examples and Templates** - Sample implementations, usage patterns?
10. **Research and Development** - Experimental features, research notes?

### Organizational Principles to Discuss:
1. **Module Boundaries** - How to define clear interfaces between components?
2. **Dependency Management** - How components should interact and depend on each other?
3. **Scalability Considerations** - How structure supports growth and evolution?
4. **Maintainability** - Code organization for long-term maintenance?
5. **Extensibility** - How new extractors and capabilities can be added?
6. **Configuration vs Code** - What should be configurable vs hardcoded?
7. **Error Handling** - Consistent error handling patterns across components?
8. **Logging Standards** - Consistent logging and debugging approaches?

### Naming Conventions:
1. **Directory Structure** - Flat vs nested organization?
2. **File Naming** - Consistent naming patterns?
3. **Component Naming** - How to name extractors, builders, servers?
4. **Configuration Naming** - Environment variables, config files?

### Integration Patterns:
1. **Plugin Architecture** - How extractors can be dynamically loaded?
2. **Event-Driven Design** - Components communication through events?
3. **Service Layer** - Clear service boundaries and APIs?
4. **Data Flow** - How data moves between components?

## Next Steps in Discussion

1. **Review and expand** the component list
2. **Define organizational principles**
3. **Design directory structure** under /v2/
4. **Plan migration strategy** from current structure
5. **Establish restructuring workflow** for future evolution rounds

## Session Notes
- **Started**: Discussion about unstructured code after evolution cycles
- **Current State**: Need holistic restructuring before continuing development
- **Decision**: Plan complete structure under /v2/ before migrating
- **Architecture Decision**: CLI-based interfaces between all components
- **Implementation Principle**: Simple Python CLI calls, no complex CLI packages
- **Documentation Requirement**: Each module needs CLAUDE.md explaining purpose and boundaries

---

*This document will be updated throughout our discussion to capture all structural decisions and rationale.*

---

## **NEW ACTION ITEMS DECIDED**

### 1. Directory Structure Creation
- Create complete directory structure under `/v2/` as planned
- **No migration yet** - just empty directories with documentation
- Each directory needs `CLAUDE.md` file explaining:
  - Purpose and role of the directory
  - What should be included
  - What should NOT be included (boundaries)
  - Relationship with other components

### 2. CLI-First Architecture
- **All component-to-component communication MUST use CLI interfaces**
- CLI advantages: no language dependencies, isolated component crashes, easy parallelization
- Use simple Python CLI calls (argparse, sys.argv) - avoid complex CLI packages
- Prefer CLI over library calls even within components when feasible

### 3. Component Interface Design
- Each component exposes CLI commands for all functionality
- Standard input/output for data transfer (JSON format preferred)
- Clear error handling and exit codes
- Version compatibility checking between components

### 4. Implementation Standards
- Stick to Python as primary language
- Simple, readable CLI commands
- Consistent command naming patterns
- Standardized help and usage documentation

---

## **NEXT STEPS**
1. Create directory structure under `/v2/`
2. Add CLAUDE.md files to each directory
3. Define CLI interfaces between components
4. Continue discussion on component boundaries and responsibilities