#!/bin/bash
# Production Deployment Script for SimFlo MCP RAG

set -e

echo "🚀 Starting SimFlo MCP RAG Production Deployment..."

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi

    # Check Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js is required but not installed"
        exit 1
    fi

    # Check npm
    if ! command -v npm &> /dev/null; then
        log_error "npm is required but not installed"
        exit 1
    fi

    log_info "All prerequisites checked ✅"
}

# Install dependencies
install_dependencies() {
    log_info "Installing dependencies..."

    # Python dependencies
    log_info "Installing Python dependencies..."
    pip install -r data-pipeline/requirements.txt

    # Node.js dependencies
    log_info "Installing Node.js dependencies..."
    npm install

    log_info "Dependencies installed ✅"
}

# Build application
build_application() {
    log_info "Building application..."

    # Build TypeScript
    npm run build

    log_info "Application built ✅"
}

# Initialize vector stores
initialize_vector_stores() {
    log_info "Initializing vector stores..."

    # Run rebuild script
    python3 scripts/rebuild_vector_stores.py

    log_info "Vector stores initialized ✅"
}

# Create environment file
create_environment_file() {
    log_info "Creating environment file..."

    if [ ! -f ".env" ]; then
        cat > .env << EOF
# Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
MCP_HOST=127.0.0.1
MCP_PORT=3000

# Logging
LOG_LEVEL=info
ENABLE_METRICS=true

# Environment
NODE_ENV=production
SERVICE_MODE=single
EOF
        log_info "Environment file created ✅"
    else
        log_warn "Environment file already exists, skipping..."
    fi
}

# Health check function
health_check() {
    log_info "Performing health check..."

    # Start API server in background
    python3 data-pipeline/api_server.py > production_server.log 2>&1 &
    API_PID=$!

    # Wait for server to start
    sleep 5

    # Check health endpoint
    if curl -s http://localhost:8000/health > /dev/null; then
        log_info "API server health check passed ✅"

        # Get health status
        curl -s http://localhost:8000/health | python3 -m json.tool

        # Stop test server
        kill $API_PID 2>/dev/null || true
        wait $API_PID 2>/dev/null || true

        return 0
    else
        log_error "API server health check failed"

        # Show logs
        log_error "Server logs:"
        tail -20 production_server.log

        # Stop test server
        kill $API_PID 2>/dev/null || true
        wait $API_PID 2>/dev/null || true

        return 1
    fi
}

# Create systemd service files
create_systemd_services() {
    log_info "Creating systemd service files..."

    # API Server service
    cat > simflo-rag-api.service << 'EOF'
[Unit]
Description=SimFlo RAG API Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/simflo-mcp-rag
ExecStart=/usr/bin/python3 data-pipeline/api_server.py --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10
Environment=PATH=/usr/bin:/usr/local/bin
Environment=LOG_LEVEL=info
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
EOF

    # MCP Server service
    cat > simflo-rag-mcp.service << 'EOF'
[Unit]
Description=SimFlo RAG MCP Server
After=network.target simflo-rag-api.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/simflo-mcp-rag
ExecStart=/usr/bin/node dist/mcp-server.js
Restart=always
RestartSec=10
Environment=PATH=/usr/bin:/usr/local/bin
Environment=MCP_HOST=0.0.0.0
Environment=MCP_PORT=3000

[Install]
WantedBy=multi-user.target
EOF

    log_info "Systemd service files created ✅"
    log_info "To install services:"
    log_info "  sudo cp simflo-rag-api.service /etc/systemd/system/"
    log_info "  sudo cp simflo-rag-mcp.service /etc/systemd/system/"
    log_info "  sudo systemctl daemon-reload"
    log_info "  sudo systemctl enable simflo-rag-api simflo-rag-mcp"
    log_info "  sudo systemctl start simflo-rag-api simflo-rag-mcp"
}

# Create Docker setup
create_docker_setup() {
    log_info "Creating Docker setup..."

    # Create Dockerfile
    cat > Dockerfile << 'EOF'
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    curl \
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

# Start API server (MCP server would run separately)
CMD ["python3", "data-pipeline/api_server.py", "--host", "0.0.0.0", "--port", "8000"]
EOF

    # Create docker-compose.yml
    cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  api-server:
    build: .
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=info
      - NODE_ENV=production
      - API_HOST=0.0.0.0
      - API_PORT=8000
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
    volumes:
      - ./rag_databases:/app/rag_databases

  mcp-server:
    build: .
    ports:
      - "3000:3000"
    environment:
      - MCP_HOST=0.0.0.0
      - MCP_PORT=3000
    depends_on:
      api-server:
        condition: service_healthy
    restart: unless-stopped
    command: ["node", "dist/mcp-server.js"]
    volumes:
      - ./rag_databases:/app/rag_databases

volumes:
  rag_databases:
EOF

    log_info "Docker setup created ✅"
    log_info "To start with Docker:"
    log_info "  docker-compose up -d"
    log_info "  docker-compose logs -f"
    log_info "  docker-compose down"
}

# Main deployment function
main() {
    log_info "Starting production deployment..."

    # Check if running as root for system installations
    if [ "$1" = "system" ] && [ "$EUID" -ne 0 ]; then
        log_error "Please run as root for system installation"
        exit 1
    fi

    check_prerequisites
    install_dependencies
    build_application
    initialize_vector_stores
    create_environment_file

    if [ "$1" = "system" ]; then
        create_systemd_services
    fi

    create_docker_setup

    # Perform health check
    if health_check; then
        log_info "Deployment completed successfully! 🎉"
        log_info ""
        log_info "Next steps:"
        log_info "1. Review the production setup guide: docs/production-setup-guide.md"
        log_info "2. Choose your deployment method:"
        log_info "   - Direct execution: python3 data-pipeline/api_server.py"
        log_info "   - Docker: docker-compose up -d"
        log_info "   - System services: (see service files above)"
        log_info "3. Test the deployment:"
        log_info "   curl http://localhost:8000/health"
        log_info "   curl http://localhost:8000/api/v1/components/search?q=button"
    else
        log_error "Deployment failed! Please check the logs above."
        exit 1
    fi
}

# Parse command line arguments
case "${1:-}" in
    "system")
        main "system"
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [system]"
        echo ""
        echo "Arguments:"
        echo "  system    Install as system services (requires root)"
        echo "  help      Show this help message"
        echo ""
        echo "Default: Deploy without system services"
        ;;
    "")
        main
        ;;
    *)
        log_error "Unknown argument: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac