# Project Brief: SimFlo MCP RAG - Universal Component Discovery System

## Executive Summary

Build a universal RAG system that enables natural language search of technical components and documentation through AI assistants using the MCP protocol. The system has evolved from a minimal shadcn component search tool to a comprehensive multi-registry platform with advanced context awareness and intelligent recommendations.

**Current Status**: MVP 4 - Enhanced Context Intelligence & Multi-Dimensional Awareness

## Problem Statement

Developers need to quickly discover components, documentation, and technical solutions while working with AI assistants. Manual search through multiple registries, documentation sites, and project files breaks workflow efficiency. The system should understand the complete development context and provide intelligent, relevant recommendations.

**Key pain points**:
- Fragmented component discovery across multiple registries
- Lack of context-aware search for development projects
- Manual research slows down AI-assisted development
- No integration between component search and project understanding

## Proposed Solution

**Universal RAG System**:
- Multi-registry component ingestion (shadcn, gluestack, radix)
- Universal search across components and documentation
- Advanced context awareness with project type detection
- Intelligent recommendations based on technology stack
- MCP protocol integration for AI assistant access

**Current Capabilities**:
- 130+ components across 3 major registries
- Web documentation ingestion and search
- Context-aware platform routing (React Native/React JS)
- 8 operational MCP tools with intelligent search
- Production-ready API server with comprehensive error handling

## Target Users

### Primary User Segment: Developers Working with AI Assistants
- React/React Native developers
- Full-stack developers
- Technical leads and architects
- Development teams using component libraries

## Goals & Success Metrics

### Business Objectives
- Reduce component discovery time from minutes to seconds
- Enable natural language technical search in AI conversations
- Provide intelligent recommendations based on project context
- Support multiple technology stacks and development patterns

### Success Criteria
- **Single command start**: `python3 data-pipeline/api_server.py`
- **Works offline** after initial indexing
- **<100MB memory usage** for typical operations
- **<1 second response time** for search queries
- **Multi-registry support** with context-aware routing
- **Universal search** across components and documentation

## Current Implementation (MVP 4)

### Core Features (Implemented)
- ✅ Multi-registry system with 130+ components
- ✅ Context-aware search with platform routing
- ✅ Universal search across components and documentation
- ✅ 8 operational MCP tools for AI assistant integration
- ✅ Advanced context engine with project type detection
- ✅ Web documentation ingestion with BeautifulSoup
- ✅ Comprehensive error handling and monitoring
- ✅ Production-ready API server with FastAPI

### Technology Stack
- **Backend**: Python 3.8+ with FastAPI framework
- **Vector Database**: ChromaDB with multi-registry architecture
- **MCP Protocol**: Python MCP SDK for AI assistant integration
- **Web Processing**: BeautifulSoup4 for documentation extraction
- **Search**: Semantic search with context-aware ranking

### Registry Support
- **shadcn_db**: 102 components from Shadcn UI registry
- **gluestack_db**: 28 components from Gluestack UI registry
- **radix_db**: Ready for ingestion (Radix UI components)
- **Documentation**: Web documentation sites and technical content

## System Architecture

### Multi-Registry Architecture
```
Multiple Sources → Specialized Extractors → Vector Stores (Per Registry) → Universal Search
     ↓                   ↓                      ↓                      ↓
Component Regs    Documentation Sites    ChromaDB Collections    Context-Aware API
     +                   +                      +                      +
Project Files     Code Examples         Search Indexing        Smart Routing
```

### Context-Aware Routing
- **React Native Context**: gluestack_db → shadcn_db → radix_db
- **React JS Context**: shadcn_db → gluestack_db → radix_db
- **Auto/None Context**: shadcn_db → gluestack_db → radix_db

### Available MCP Tools
1. **search_components** - Search for components by query
2. **get_component_details** - Get detailed component information
3. **list_components** - List all available components
4. **get_component_installation** - Get installation commands
5. **set_platform_context** - Switch between React Native/React JS/Auto/None
6. **get_context_suggestions** - Get context suggestions for queries
7. **get_context_stats** - Get context usage statistics
8. **universal_search** - Search across components and documentation

## Current MVP Status: MVP 4 - Enhanced Context Intelligence

### In Development: Multi-Dimensional Context Awareness
- **Technology Stack Detection**: React, Vue, Angular, Node.js, Python, etc.
- **Environmental Context**: Testing frameworks, styling, deployment tools
- **Intelligent Recommendations**: Context-aware component suggestions
- **Integration Guidance**: Step-by-step integration assistance
- **Best Practice Matching**: Recommendations based on detected patterns

### Success Metrics for MVP 4
- 10+ context dimensions successfully detected
- 20+ technologies accurately recognized
- 40%+ improvement in search relevance with rich context
- 80%+ accuracy in component recommendations

## Technical Implementation

### Key Files
- **API Server**: `data-pipeline/api_server.py` - FastAPI server with MCP integration
- **Context Engine**: `data-pipeline/context_manager.py` - Multi-dimensional context awareness
- **Registry Manager**: `data-pipeline/registry_manager.py` - Multi-registry management
- **Extractors**: `data-pipeline/extractors/` - Specialized data source processors
- **Vector Stores**: `rag_databases/*/` - ChromaDB collections per registry

### Development Workflow
1. **Start Server**: `python3 data-pipeline/api_server.py`
2. **Test Search**: Use API endpoints or MCP tools
3. **Add Registries**: Extend extractor system
4. **Enhance Context**: Develop new context dimensions
5. **Iterate**: Build, test, and deploy incrementally

## Constraints & Assumptions

### Constraints
- **Local Development**: Focused on local developer workflow
- **Python-Based**: Built with Python ecosystem for rapid development
- **MCP Protocol**: Uses standard MCP for AI assistant integration
- **Community Registries**: Leverages existing component libraries

### Key Assumptions
- Component registries follow predictable structures
- Projects use common configuration files (package.json, etc.)
- AI assistants support MCP protocol integration
- Local development environment with standard tooling

## Future Vision: Universal Development Assistant

The system evolves toward comprehensive development assistance:
- **Multi-Source Ingestion**: GitHub, documentation sites, APIs
- **Rich Context Understanding**: Complete technology stack awareness
- **Intelligent Recommendations**: Best practices and integration patterns
- **IDE Integration**: Direct development environment integration
- **Collaborative Features**: Team knowledge sharing and patterns

## Next Steps

### Immediate Actions
1. Complete MVP 4 enhanced context intelligence
2. Implement technology stack detection system
3. Build recommendation engine with compatibility matrices
4. Add integration guidance capabilities

### Development Approach
- **Iterative**: Build small, testable increments
- **User-Focused**: Solve real developer problems
- **Extensible**: Plugin architecture for new data sources
- **Local-First**: Optimize for individual developer workflow

This project represents the evolution from a simple component search tool to an intelligent development assistant that understands the complete development ecosystem and provides contextual, actionable guidance across all aspects of software development.