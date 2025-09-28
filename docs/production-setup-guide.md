# SimFlo MCP RAG - Production Setup Guide

## Overview

This guide provides instructions for deploying and maintaining the SimFlo MCP RAG system in production environments. The system provides universal component discovery through natural language search across multiple registries.

## System Architecture

### Core Components

1. **API Server** (`data-pipeline/api_server.py`)
   - FastAPI-based HTTP server
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

4. **MCP Server** (`dist/mcp-server.js`)
   - TypeScript-based MCP protocol server
   - Integrates with AI assistants
   - Provides 7 operational tools

## Prerequisites

### System Requirements
- **OS**: Linux, macOS, or Windows
- **Python**: 3.8 or higher
- **Node.js**: 16 or higher
- **Memory**: Minimum 2GB RAM, 4GB recommended
- **Storage**: Minimum 1GB free space

### Dependencies
```bash
# Python dependencies
pip install fastapi uvicorn chromadb python-dotenv

# Node.js dependencies
npm install typescript @types/node @modelcontextprotocol/sdk
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

### 3. Install Node.js Dependencies
```bash
npm install
npm run build
```

### 4. Initialize Vector Stores
```bash
# Rebuild vector stores with enhanced metadata
python3 scripts/rebuild_vector_stores.py
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
MCP_HOST=127.0.0.1
MCP_PORT=3000

# Logging
LOG_LEVEL=info
ENABLE_METRICS=true

# Development vs Production
NODE_ENV=production
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

## Production Deployment

### Option 1: Direct Server Execution

#### API Server
```bash
# Start API server
python3 data-pipeline/api_server.py --host 0.0.0.0 --port 8000
```

#### MCP Server
```bash
# Start MCP server
node dist/mcp-server.js
```

### Option 2: Using Docker

#### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY . .

# Install Python dependencies
RUN pip install -r data-pipeline/requirements.txt

# Install Node.js dependencies and build
RUN npm install && npm run build

# Rebuild vector stores
RUN python3 scripts/rebuild_vector_stores.py

# Expose ports
EXPOSE 8000 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start both servers
CMD ["sh", "-c", "python3 data-pipeline/api_server.py & node dist/mcp-server.js"]
```

#### Build and Run
```bash
# Build Docker image
docker build -t simflo-mcp-rag .

# Run container
docker run -d \
  --name simflo-rag \
  -p 8000:8000 \
  -p 3000:3000 \
  simflo-mcp-rag
```

### Option 3: Using Docker Compose

#### docker-compose.yml
```yaml
version: '3.8'

services:
  api-server:
    build: .
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=info
      - NODE_ENV=production
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  mcp-server:
    build: .
    ports:
      - "3000:3000"
    environment:
      - MCP_HOST=0.0.0.0
      - MCP_PORT=3000
    depends_on:
      - api-server
    restart: unless-stopped
```

#### Start Services
```bash
docker-compose up -d
```

## Monitoring and Health Checks

### Health Check Endpoints

#### API Server Health
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
    "status": "healthy",
    "timestamp": "2025-09-28T19:58:04.105174",
    "version": "2.0.0",
    "registries": {
        "shadcn_db": {
            "status": "healthy",
            "component_count": 80,
            "platforms": ["reactjs"]
        },
        "gluestack_db": {
            "status": "healthy",
            "component_count": 28,
            "platforms": ["reactjs", "react-native"]
        },
        "radix_db": {
            "status": "empty",
            "component_count": 0,
            "platforms": []
        }
    },
    "summary": {
        "total_registries": 3,
        "healthy_registries": 2,
        "total_components": 108,
        "cache_size": 0
    }
}
```

#### Registry Status
```bash
curl http://localhost:8000/api/v1/registries
```

### Log Monitoring

#### API Server Logs
```bash
# View logs
tail -f server_enhanced.log

# Filter for errors
grep "ERROR" server_enhanced.log

# Monitor health checks
grep "health" server_enhanced.log
```

#### System Metrics
Monitor:
- Memory usage
- CPU utilization
- Disk space
- Network connectivity
- Response times

## API Usage

### Search Components
```bash
# Basic search
curl "http://localhost:8000/api/v1/components/search?q=button&limit=5"

# With platform filtering
curl "http://localhost:8000/api/v1/components/search?q=button&platform=reactjs"

# With registry filtering
curl "http://localhost:8000/api/v1/components/search?q=button&registry=shadcn_db"
```

### Response Format
```json
{
    "success": true,
    "data": [
        {
            "name": "button",
            "type": "ui",
            "description": "Shadcn UI button component",
            "relevanceScore": 0.0,
            "installCommand": "npm install react class-variance-authority @radix-ui/react-slot @/lib/utils",
            "registry": "https://github.com/shadcn-ui/ui",
            "platform": ["reactjs"],
            "categories": ["components"],
            "dependencies": [],
            "registryDependencies": []
        }
    ],
    "error": null
}
```

## Maintenance

### Updating Component Libraries

#### 1. Update Registry Data
```bash
# Run extractors for updated components
npm run extract:shadcn
npm run extract:gluestack
npm run extract:radix
```

#### 2. Rebuild Vector Stores
```bash
# Rebuild with new data
python3 scripts/rebuild_vector_stores.py
```

#### 3. Verify Health
```bash
# Check system health
curl http://localhost:8000/health
```

### Backup and Recovery

#### Backup Vector Stores
```bash
# Backup the entire rag_databases directory
tar -czf rag_databases_backup_$(date +%Y%m%d).tar.gz rag_databases/
```

#### Restore from Backup
```bash
# Stop servers
docker-compose down

# Restore backup
tar -xzf rag_databases_backup_20250928.tar.gz

# Restart services
docker-compose up -d
```

### Performance Tuning

#### Vector Store Optimization
- Monitor collection sizes and consider splitting if >10,000 components
- Regular cleanup of old/unused data
- Optimize embedding models for better search relevance

#### API Server Tuning
- Adjust worker counts based on load
- Implement caching layers for frequent queries
- Monitor response times and optimize slow queries

## Security Considerations

### Network Security
- Use firewalls to restrict access to API ports
- Implement HTTPS/TLS for production deployments
- Consider using API gateway for rate limiting

### Data Protection
- Regular backups of vector stores
- Monitor for unusual access patterns
- Implement authentication if needed

### Environment Security
- Keep dependencies updated
- Use specific versions in requirements
- Monitor security advisories

## Troubleshooting

### Common Issues

#### Empty Search Results
```bash
# Check registry health
curl http://localhost:8000/health

# Rebuild vector stores if needed
python3 scripts/rebuild_vector_stores.py
```

#### Server Start Errors
```bash
# Check port availability
netstat -tulpn | grep :8000

# Check logs for errors
tail -f server_enhanced.log
```

#### Memory Issues
```bash
# Monitor memory usage
free -h

# Restart services if needed
docker-compose restart
```

### Performance Issues
- Monitor response times
- Check for memory leaks
- Optimize search queries
- Consider scaling horizontally

## Support

For issues and questions:
1. Check this documentation
2. Review system logs
3. Test health endpoints
4. Check GitHub issues

## Version History

- **v2.0.0**: Production release with enhanced metadata, error handling, and monitoring
- **v1.0.0**: Initial MVP release

---

**Note**: This guide assumes you have completed MVP 2 development and have a working multi-registry system with shadcn, gluestack, and radix component libraries.