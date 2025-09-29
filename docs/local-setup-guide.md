# SimFlo MCP RAG - Local Development Setup Guide

## Overview

This guide provides instructions for setting up and running the SimFlo MCP RAG system for local development. The system provides universal component discovery through natural language search across multiple registries with advanced context awareness.

## System Architecture

### Core Components

1. **API Server** (`data-pipeline/api_server.py`)
   - FastAPI-based HTTP server with MCP integration
   - Provides RESTful API for component search and retrieval
   - Enhanced with comprehensive error handling and monitoring

2. **Registry Manager** (`data-pipeline/registry_manager.py`)
   - Multi-registry management system
   - Handles shadcn, gluestack, and radix registries
   - Platform-aware component routing

3. **Vector Stores** (`rag_databases/*_db/chroma_db/`)
   - ChromaDB collections for each registry
   - Semantic search capabilities
   - Metadata-enriched component indexing

4. **Context Engine** (`data-pipeline/context_manager.py`)
   - Multi-dimensional context awareness
   - Project type detection and routing
   - Session management and history tracking

## Prerequisites

### System Requirements
- **OS**: Linux, macOS, or Windows
- **Python**: 3.8 or higher
- **Memory**: Minimum 2GB RAM, 4GB recommended
- **Storage**: Minimum 1GB free space

### Dependencies
```bash
# Python dependencies
pip install fastapi uvicorn chromadb requests beautifulsoup4

# Optional: For development
pip install python-dotenv pytest pytest-asyncio
```

## Installation

### 1. Clone and Setup Repository
```bash
git clone <repository-url>
cd simflo-mcp-rag
```

### 2. Install Python Dependencies
```bash
cd data-pipeline
pip install -r requirements.txt
cd ..
```

### 3. Initialize Vector Stores
```bash
# Rebuild vector stores with enhanced metadata
python3 scripts/rebuild_vector_stores.py
```

## Configuration

### Environment Variables

Create a `.env` file in the project root (optional):

```env
# Server Configuration
API_HOST=127.0.0.1
API_PORT=8000

# Logging
LOG_LEVEL=info
ENABLE_METRICS=true

# Development Mode
SERVICE_MODE=single
```

### Registry Configuration

Registries are configured in the `rag_databases/` directory:

```
rag_databases/
├── shadcn_db/
│   ├── components.json
│   └── chroma_db/
├── gluestack_db/
│   ├── components.json
│   └── chroma_db/
└── radix_db/
    ├── components.json
    └── chroma_db/
```

## Quick Start

### Start the API Server
```bash
# Start API server (default port 8000)
python3 data-pipeline/api_server.py

# Start on specific port
python3 data-pipeline/api_server.py --port 8001

# Start with specific host
python3 data-pipeline/api_server.py --host 127.0.0.1
```

### Health Check
```bash
# Check if server is running
curl http://localhost:8000/health

# Expected response:
{
    "status": "healthy",
    "timestamp": "2025-09-28T19:58:04.105174",
    "version": "2.0.0",
    "registries": {
        "shadcn_db": {"status": "healthy", "component_count": 102, "platforms": ["reactjs"]},
        "gluestack_db": {"status": "healthy", "component_count": 28, "platforms": ["reactjs", "react-native"]},
        "radix_db": {"status": "empty", "component_count": 0, "platforms": []}
    },
    "summary": {
        "total_registries": 3,
        "healthy_registries": 2,
        "total_components": 130,
        "cache_size": 0
    }
}
```

## API Usage

### Search Components
```bash
# Basic search
curl "http://localhost:8000/api/v2/search/universal?q=button"

# With platform filtering
curl "http://localhost:8000/api/v2/search/universal?q=button&platform=reactjs"

# Universal search (components + documentation)
curl "http://localhost:8000/api/v2/search/universal?q=form validation"
```

### Context Management
```bash
# Get context statistics
curl http://localhost:8000/api/v2/context/stats

# Get context suggestions
curl http://localhost:8000/api/v2/context/suggestions

# Detect project context
curl -X POST http://localhost:8000/api/v2/context/detect \
  -H "Content-Type: application/json" \
  -d '{"project_path": "/path/to/project"}'
```

### Component Details
```bash
# Get component details
curl http://localhost:8000/api/v2/components/button

# Get installation information
curl http://localhost:8000/api/v2/components/button/installation

# List all components
curl http://localhost:8000/api/v2/components
```

## MCP Tools Integration

The system automatically starts MCP server alongside the API server. Available tools:

### Context Management Tools
- `set_platform_context` - Switch between React Native/React JS/Auto/None
- `get_context_suggestions` - Get context suggestions for queries
- `get_context_stats` - Get context usage statistics

### Component Search Tools
- `search_components` - Search for components by query
- `get_component_details` - Get detailed component information
- `list_components` - List all available components
- `get_component_installation` - Get installation commands

### Universal Search
- `universal_search` - Search across components and documentation

## Development Workflow

### Rebuilding Vector Stores
```bash
# Rebuild all vector stores
python3 scripts/rebuild_vector_stores.py

# Rebuild specific registry
python3 scripts/rebuild_vector_stores.py --registry shadcn_db
```

### Testing the System
```bash
# Test basic search functionality
curl "http://localhost:8000/api/v2/search/universal?q=button&limit=5"

# Test context switching
curl -X POST http://localhost:8000/api/v2/context/detect \
  -H "Content-Type: application/json" \
  -d '{"project_path": "/path/to/react/project"}'

# Test universal search
curl "http://localhost:8000/api/v2/search/universal?q=how to use forms"
```

### Monitoring and Logs

#### View Server Logs
```bash
# Server outputs to console
tail -f server.log  # if logging to file
```

#### Monitor Performance
- **Memory Usage**: Typically <100MB for normal operations
- **Response Time**: <1 second for search queries
- **Registry Health**: Check `/health` endpoint regularly

## Troubleshooting

### Common Issues

#### Server Won't Start
```bash
# Check Python version (3.8+ required)
python3 --version

# Check dependencies
pip list | grep -E "fastapi|uvicorn|chromadb"

# Check port availability
netstat -tulpn | grep :8000
```

#### Empty Search Results
```bash
# Check registry health
curl http://localhost:8000/health

# Rebuild vector stores if needed
python3 scripts/rebuild_vector_stores.py
```

#### Context API Issues
```bash
# Test context detection
curl -X POST http://localhost:8000/api/v2/context/detect \
  -H "Content-Type: application/json" \
  -d '{"project_path": "/path/to/your/project"}'

# Check context stats
curl http://localhost:8000/api/v2/context/stats
```

### Performance Issues
- **Memory Usage**: Monitor with system tools
- **Response Time**: Should be <1 second for typical queries
- **Large Registries**: Consider splitting if >10,000 components

## File Structure

```
simflo-mcp-rag/
├── data-pipeline/
│   ├── api_server.py              # Main API server
│   ├── context_manager.py         # Context engine
│   ├── registry_manager.py        # Registry management
│   ├── extractors/                # Data source extractors
│   └── scripts/                   # Utility scripts
├── rag_databases/                 # Vector stores and data
│   ├── shadcn_db/
│   ├── gluestack_db/
│   └── radix_db/
├── docs/                          # Documentation
└── current_mvp.txt               # Current MVP version
```

## Current System Status

### Available Registries
- **shadcn_db**: 102 components (reactjs)
- **gluestack_db**: 28 components (reactjs, react-native)
- **radix_db**: Ready for ingestion

### MCP Tools: All 8 Operational
- Component search and retrieval
- Context management and awareness
- Universal search across sources
- Installation guidance

### System Capabilities
- ✅ Multi-registry search with 130+ components
- ✅ Context-aware routing and recommendations
- ✅ Universal search (components + documentation)
- ✅ Advanced project type detection
- ✅ Comprehensive error handling and monitoring

## Next Steps for Development

### MVP 4 Enhancement
1. **Technology Stack Detection**: Extend context engine
2. **Intelligent Recommendations**: Build suggestion system
3. **Integration Guidance**: Add step-by-step assistance
4. **Best Practice Matching**: Recommend patterns based on stack

### Adding New Registries
1. Create extractor in `data-pipeline/extractors/`
2. Register in `registry_manager.py`
3. Add to configuration
4. Rebuild vector stores

## Support

For issues and questions:
1. Check this documentation
2. Review system logs
3. Test health endpoints
4. Verify dependencies are installed

---

**Note**: This guide focuses on local development. For production deployment considerations, refer to the architecture documentation and project brief.

**Current Version**: MVP 4 - Enhanced Context Intelligence & Multi-Dimensional Awareness