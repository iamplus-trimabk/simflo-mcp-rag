# Quick Reference Guide

This guide provides essential information for using and understanding the SimFlo MCP RAG system.

## Quick Start

### Starting the System
```bash
# Start the API server
python3 data-pipeline/api_server.py

# Server runs on http://localhost:8000
# MCP server also starts automatically
```

### Basic Usage
```bash
# Search for components via API
curl "http://localhost:8000/api/v2/search/universal?q=button&platform=reactjs"

# Get system health
curl "http://localhost:8000/health"
```

## Core Architecture

### System Components
```
Data Sources → Extractors → Vector Stores → Search API → MCP Tools
     ↓              ↓              ↓              ↓          ↓
GitHub + Web   Processing    ChromaDB      Context-Aware   AI Assistant
Documentation              Collections    Search         Integration
```

### Available Registries
- **shadcn_db**: Shadcn/UI components (102 components)
- **gluestack_db**: Gluestack UI components (28 components)
- **radix_db**: Radix UI components (ready for ingestion)

## MCP Tools Available

### Context Management
- `set_platform_context` - Switch between React Native/React JS/Auto/None
- `get_context_suggestions` - Get context suggestions for queries
- `get_context_stats` - Get context usage statistics

### Component Search
- `search_components` - Search for components by query
- `get_component_details` - Get detailed component information
- `list_components` - List all available components
- `get_component_installation` - Get installation commands

### Universal Search (MVP 3+)
- `universal_search` - Search across components and documentation

## API Endpoints

### Search Endpoints
```bash
# Universal search (components + documentation)
GET /api/v2/search/universal?q={query}&platform={platform}

# Contextual search
POST /api/v2/search/contextual

# Context management
GET /api/v2/context/stats
POST /api/v2/context/detect
GET /api/v2/context/suggestions
```

### Component Endpoints
```bash
# Component details
GET /api/v2/components/{component_name}

# Installation info
GET /api/v2/components/{component_name}/installation

# List components
GET /api/v2/components
```

### System Endpoints
```bash
# Health check
GET /health

# Available registries
GET /api/v2/registries
```

## Context System

### Platform Contexts
- **reactnative**: React Native development (mobile apps)
- **reactjs**: React JS development (web apps)
- **auto**: Automatic context detection
- **none**: No specific context

### Context-Aware Routing
- React Native context → Prioritizes gluestack_db
- React JS context → Prioritizes shadcn_db
- Auto context → Searches all registries
- None context → Searches all registries

## Search Capabilities

### Search Strategies
- **Exact Match**: Precise component name matching
- **Semantic**: Natural language understanding
- **Cross-Category**: Search across all component types
- **Weighted Blend**: Balanced approach (default)

### Filtering Options
- **Platform**: reactjs, reactnative
- **Registry**: shadcn_db, gluestack_db, radix_db
- **Category**: components, hooks, blocks
- **Quality Threshold**: Minimum quality score (0.0-1.0)

## Data Models

### Component Structure
```json
{
  "name": "button",
  "display_name": "Button",
  "description": "A button component",
  "component_type": "component",
  "category": "components",
  "source_url": "https://github.com/...",
  "documentation_url": "https://docs.example.com/...",
  "dependencies": ["@radix-ui/react-slot"],
  "quality_score": 0.9,
  "platforms": ["reactjs", "reactnative"]
}
```

### Search Response
```json
{
  "success": true,
  "data": {
    "results": [...],
    "total_results": 10,
    "query_info": {
      "query": "button",
      "platform": "reactjs",
      "context": "reactjs"
    }
  }
}
```

## Configuration

### Environment Variables
```bash
# Server Configuration
SERVICE_MODE=single
LOGIC_SERVICE_PORT=3001
LOGIC_SERVICE_HOST=localhost
LOG_LEVEL=info

# Theme (for UI components)
UI_THEME=auto
ENABLE_METRICS=true
```

### Context Configuration
Context mappings are managed in `context_manager.py` with configurable registry priorities per platform context.

## Development Workflow

### Adding New Data Sources
1. Create extractor in `data-pipeline/extractors/`
2. Register in `extractor_factory.py`
3. Add to registry configuration
4. Test with validation scripts

### Testing the System
```bash
# Test context engine
python3 scripts/test_context_engine.py

# Test context API
python3 scripts/test_context_api.py

# Test search functionality
python3 scripts/test_search.py
```

## Common Commands

### System Operations
```bash
# Start server
python3 data-pipeline/api_server.py

# Run tests
python3 scripts/test_*.py

# Check logs
tail -f api_server.log
```

### MCP Integration
The system automatically starts MCP server alongside the API server. Available tools can be accessed through MCP-compatible AI assistants.

## Troubleshooting

### Common Issues

**Server Won't Start**
- Check port 8000 is available
- Verify Python dependencies are installed
- Check for syntax errors in configuration files

**No Search Results**
- Verify vector stores are populated
- Check registry configurations
- Ensure context is properly set

**Context Issues**
- Verify context manager is initialized
- Check platform context values
- Review context mappings in configuration

### Performance Tips
- Use specific search terms for better results
- Set appropriate quality thresholds
- Leverage platform context for better relevance
- Cache frequently accessed components

## System Requirements

### Minimum Requirements
- Python 3.8+
- 100MB RAM for basic operation
- ChromaDB for vector storage
- Internet connection for web scraping (MVP 3+)

### Recommended Setup
- Python 3.9+
- 200MB RAM for optimal performance
- SSD for faster vector operations
- Stable internet connection for documentation ingestion

## Current Status (MVP 4)

### Active Development
- Enhanced context intelligence with technology stack detection
- Multi-dimensional context awareness
- Smart recommendations and integration guidance

### System Capabilities
- Universal search across components and documentation
- Platform-aware component recommendations
- Contextual relevance scoring
- Multi-registry management

### Next Steps
- Advanced technology stack detection
- Rich context dimensions (testing, deployment, build tools)
- Intelligent search with smart recommendations

---

This quick reference provides the essential information for using the SimFlo MCP RAG system. For detailed development information and future roadmap, refer to `docs/future/future_plan.md` and `docs/mvp_4/mvp_4_plan.md`.