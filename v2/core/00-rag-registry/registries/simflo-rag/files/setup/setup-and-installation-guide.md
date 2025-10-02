# Setup and Installation Guide

## Purpose
Comprehensive guide for setting up and installing SimFlo RAG v2, covering system requirements, installation steps, configuration, and verification procedures for AI assistants and developers.

## System Requirements

### Hardware Requirements
- **Processor**: x86_64 or ARM64 architecture
- **Memory**: Minimum 4GB RAM, 8GB+ recommended
- **Storage**: Minimum 10GB available space
- **Network**: Internet connection for content fetching

### Software Requirements

#### Operating System Support
- **Linux**: Ubuntu 20.04+, Debian 11+, CentOS 8+, Fedora 35+
- **macOS**: macOS 11.0+ (Big Sur or later)
- **Windows**: Windows 10/11 with WSL2 (Windows Subsystem for Linux)

#### Required Software
- **Python**: Version 3.8 or higher (3.9+ recommended)
- **Git**: For version control and repository operations
- **GitHub CLI**: For repository content fetching (`gh` command)
- **Node.js**: Version 16+ (for some content processing tasks)
- **SQLite**: Version 3.35+ (for local registry databases)

#### Optional Software
- **PostgreSQL**: Version 13+ (for production registry databases)
- **Redis**: Version 6+ (for caching and session management)
- **Docker**: Version 20+ (for containerized deployments)

## Quick Installation

### One-Line Installation (Linux/macOS)
```bash
# Install SimFlo RAG v2 with automatic dependency detection
curl -sSL https://raw.githubusercontent.com/simflo-rag/v2/main/scripts/install.sh | bash

# Or download and run manually
wget https://raw.githubusercontent.com/simflo-rag/v2/main/scripts/install.sh
chmod +x install.sh
./install.sh
```

### Windows Installation (WSL2)
```powershell
# Enable WSL2 if not already enabled
wsl --install

# In WSL2 Ubuntu terminal, run installation
curl -sSL https://raw.githubusercontent.com/simflo-rag/v2/main/scripts/install.sh | bash
```

## Manual Installation

### Step 1: Clone Repository
```bash
# Clone the SimFlo RAG v2 repository
git clone https://github.com/simflo-rag/v2.git
cd v2

# Verify repository structure
ls -la v2/
```

### Step 2: Install Python Dependencies
```bash
# Install Python package dependencies
pip install -r requirements.txt

# Install system-specific dependencies
python3 scripts/install_dependencies.py

# Verify installation
python3 -c "import chromadb; print('ChromaDB installed successfully')"
```

### Step 3: Install Required Tools

#### Install GitHub CLI
```bash
# macOS
brew install gh

# Ubuntu/Debian
sudo apt install gh

# Fedora/CentOS
sudo dnf install gh  # or yum install gh

# Authenticate with GitHub
gh auth login

# Verify installation
gh --version
```

#### Install Node.js (if not present)
```bash
# Using NodeSource repository (recommended)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Or using version manager
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 18
nvm use 18

# Verify installation
node --version
npm --version
```

### Step 4: Configure Environment
```bash
# Copy environment configuration template
cp .env.example .env

# Edit configuration file
nano .env
```

**Environment Configuration (.env)**:
```bash
# Content Storage Configuration
CONTENT_ROOT=/content
SIMFLO_RAG_HOME=/path/to/simflo-rag/v2

# Database Configuration
DEFAULT_DB_TYPE=sqlite
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=simflo
POSTGRES_PASSWORD=your_password
POSTGRES_DB=simflo_rag

# Redis Configuration (Optional)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# GitHub Configuration
GITHUB_TOKEN=your_github_token_here

# System Configuration
MAX_CONCURRENT_EXTRACTORS=4
DEFAULT_TIMEOUT=300
ENABLE_PARALLEL_PROCESSING=true

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=/var/log/simflo-rag.log
```

### Step 5: Initialize System
```bash
# Create necessary directories
mkdir -p $CONTENT_ROOT/github
mkdir -p $SIMFLO_RAG_HOME/data/registries
mkdir -p $SIMFLO_RAG_HOME/logs

# Set up command aliases
source v2/commands.sh

# Add to shell profile for persistence
echo 'source /path/to/simflo-rag/v2/commands.sh' >> ~/.zshrc  # Zsh
echo 'source /path/to/simflo-rag/v2/commands.sh' >> ~/.bashrc  # Bash

# Verify installation
simflo_setup
```

## Verification and Testing

### Basic System Check
```bash
# Test all core components
simflo_setup

# Expected output:
# ✅ Registry System: OK (3 registries available)
# ✅ MCP Server: OK (18 commands available)
# ✅ Content Collection: OK (4 source types supported)
# ✅ Extractors: OK (11 extractors active)
# ✅ RAG Builder: OK (3 profiles available)
```

### Component-Specific Tests
```bash
# Test registry system
rag_registry_status
rag_registry list

# Test MCP server
mcp_search "button" --limit 3
mcp_list_registries

# Test content collection
content_status
content_list_source_types

# Test extractors
extractors_status
extractors_list
```

### Run Complete Test Suite
```bash
# Run all tests
simflo_test

# Run specific component tests
simflo_test registry
simflo_test mcp
simflo_test content
simflo_test extractors
```

## First-Time Setup

### Initialize Base Registries
```bash
# Create initial simflo-rag registry with documentation
python3 v2/core/00-rag-registry/registry.py create \
  --name simflo-rag \
  --type documentation \
  --source-dir v2/core/00-rag-registry/registries/simflo-rag/files/

# Build the registry database
python3 v2/core/00-rag-registry/registry.py rebuild-db \
  --registry simflo-rag \
  --format json

# Verify registry creation
rag_registry_info --name simflo-rag
rag_registry_search --query "CLI commands" --registry simflo-rag --limit 5
```

### Test Content Collection
```bash
# Discover component libraries
content_discover --query "shadcn ui components" --source-type github --limit 3

# Fetch content for testing
content_fetch --source "https://github.com/shadcn-ui/ui" --output-dir $CONTENT_ROOT/github/shadcn-ui/

# Test extraction
extractors_run shadcn --source-type local --source-path $CONTENT_ROOT/github/shadcn-ui/ --output-dir extracted/shadcn/
```

## Configuration Options

### Content Storage Configuration
```bash
# Set custom content root directory
export CONTENT_ROOT=/custom/content/path

# Configure multiple content directories
export CONTENT_ROOTS="/primary/content:/secondary/content:/backup/content"

# Set content retention policies
export CONTENT_RETENTION_DAYS=30
export CONTENT_MAX_SIZE_GB=50
```

### Database Configuration

#### SQLite Configuration (Default)
```bash
# SQLite database location
export SQLITE_DB_PATH=$SIMFLO_RAG_HOME/data/registries

# Database optimization settings
export SQLITE_CACHE_SIZE=2000
export SQLITE_TEMP_STORE=memory
```

#### PostgreSQL Configuration (Production)
```bash
# PostgreSQL connection settings
export POSTGRES_CONNECTION_STRING="postgresql://user:password@localhost:5432/simflo_rag"

# Connection pool settings
export POSTGRES_POOL_SIZE=10
export POSTGRES_MAX_OVERFLOW=20

# Performance settings
export POSTGRES_STATEMENT_TIMEOUT=30000
```

### Performance Configuration
```bash
# Parallel processing settings
export MAX_CONCURRENT_EXTRACTORS=8
export MAX_CONCURRENT_FETCHES=4
export PARALLEL_THRESHOLD=5

# Memory and timeout settings
export DEFAULT_TIMEOUT=600
export MAX_MEMORY_USAGE_GB=4
export CHUNK_SIZE=1000
```

## Production Setup

### Systemd Service Configuration
```bash
# Create systemd service file
sudo nano /etc/systemd/system/simflo-rag.service
```

**Systemd Service Configuration**:
```ini
[Unit]
Description=SimFlo RAG v2 Service
After=network.target

[Service]
Type=simple
User=simflo
Group=simflo
WorkingDirectory=/opt/simflo-rag/v2
Environment=CONTENT_ROOT=/opt/simflo-rag/content
Environment=SIMFLO_RAG_HOME=/opt/simflo-rag/v2
ExecStart=/usr/bin/python3 /opt/simflo-rag/v2/scripts/server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable simflo-rag
sudo systemctl start simflo-rag
sudo systemctl status simflo-rag
```

### Nginx Reverse Proxy Configuration
```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/simflo-rag
```

**Nginx Configuration**:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://localhost:8080/api/;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
```

### Docker Installation
```bash
# Build Docker image
docker build -t simflo-rag:v2 .

# Run container with volume mounts
docker run -d \
  --name simflo-rag \
  -p 8080:8080 \
  -v /opt/simflo-rag/content:/content \
  -v /opt/simflo-rag/data:/data \
  -e CONTENT_ROOT=/content \
  -e SIMFLO_RAG_HOME=/app \
  simflo-rag:v2

# Docker Compose deployment
docker-compose up -d
```

**Dockerfile**:
```dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install GitHub CLI
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && apt-get update && apt-get install -y gh

# Set working directory
WORKDIR /app

# Copy application files
COPY . /app/

# Install Python dependencies
RUN pip install -r requirements.txt

# Create necessary directories
RUN mkdir -p /content /data

# Set environment variables
ENV CONTENT_ROOT=/content
ENV SIMFLO_RAG_HOME=/app

# Expose port
EXPOSE 8080

# Run application
CMD ["python3", "scripts/server.py"]
```

## Troubleshooting

### Common Installation Issues

#### Python Version Compatibility
```bash
# Check Python version
python3 --version

# If version < 3.8, upgrade Python
sudo apt update
sudo apt install python3.9 python3.9-pip python3.9-venv

# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### GitHub CLI Authentication
```bash
# Check GitHub CLI status
gh auth status

# Re-authenticate if needed
gh auth login

# Test GitHub API access
gh api user
```

#### Permission Issues
```bash
# Fix directory permissions
sudo chown -R $USER:$USER $SIMFLO_RAG_HOME
sudo chown -R $USER:$USER $CONTENT_ROOT

# Fix script permissions
chmod +x v2/scripts/*.sh
chmod +x v2/commands.sh
```

#### Database Connection Issues
```bash
# Test SQLite database creation
python3 -c "
import sqlite3
import os
db_path = os.path.expanduser('~/test.db')
conn = sqlite3.connect(db_path)
print('SQLite connection successful')
conn.close()
"

# Test PostgreSQL connection (if configured)
python3 -c "
import psycopg2
try:
    conn = psycopg2.connect('postgresql://user:password@localhost/test')
    print('PostgreSQL connection successful')
    conn.close()
except Exception as e:
    print(f'PostgreSQL connection failed: {e}')
"
```

### Performance Issues

#### Memory Usage Optimization
```bash
# Monitor memory usage
free -h
ps aux --sort=-%mem | head -10

# Configure memory limits
export MAX_MEMORY_USAGE_GB=2
export SQLITE_CACHE_SIZE=1000
```

#### Disk Space Management
```bash
# Check disk usage
df -h
du -sh $CONTENT_ROOT
du -sh $SIMFLO_RAG_HOME/data

# Clean up old content
find $CONTENT_ROOT -type f -mtime +30 -delete
find $SIMFLO_RAG_HOME/logs -name "*.log" -mtime +7 -delete
```

### Network Issues

#### GitHub API Rate Limiting
```bash
# Configure GitHub token for higher rate limits
export GITHUB_TOKEN=your_personal_access_token

# Test rate limit status
gh api rate_limit
```

#### Content Fetching Failures
```bash
# Test network connectivity
curl -I https://github.com
ping github.com

# Configure proxy if needed
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
```

## Maintenance and Updates

### Regular Maintenance Tasks
```bash
# Create maintenance script
cat > maintenance.sh << 'EOF'
#!/bin/bash

echo "Starting SimFlo RAG maintenance..."

# Clean old content
find $CONTENT_ROOT -type f -mtime +30 -delete

# Clean old logs
find $SIMFLO_RAG_HOME/logs -name "*.log" -mtime +7 -delete

# Update registries
rag_registry_rebuild --registry simflo-rag

# Run system tests
simflo_test

echo "Maintenance completed."
EOF

chmod +x maintenance.sh

# Schedule with cron (weekly maintenance)
crontab -e
# Add line: 0 2 * * 0 /path/to/maintenance.sh >> /var/log/simflo-rag-maintenance.log 2>&1
```

### System Updates
```bash
# Update SimFlo RAG
git pull origin main
pip install -r requirements.txt --upgrade

# Update dependencies
pip install --upgrade -r requirements.txt

# Restart services (if running as service)
sudo systemctl restart simflo-rag
```

### Backup and Recovery
```bash
# Backup script
cat > backup.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/backup/simflo-rag/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Backup configuration
cp $SIMFLO_RAG_HOME/.env $BACKUP_DIR/
cp -r $SIMFLO_RAG_HOME/v2 $BACKUP_DIR/

# Backup data
cp -r $SIMFLO_RAG_HOME/data $BACKUP_DIR/
cp -r $CONTENT_ROOT $BACKUP_DIR/

# Compress backup
tar -czf "$BACKUP_DIR.tar.gz" -C "$(dirname $BACKUP_DIR)" "$(basename $BACKUP_DIR)"
rm -rf $BACKUP_DIR

echo "Backup completed: $BACKUP_DIR.tar.gz"
EOF

chmod +x backup.sh
```

This comprehensive setup and installation guide provides complete instructions for deploying SimFlo RAG v2 in various environments, from development to production setups.