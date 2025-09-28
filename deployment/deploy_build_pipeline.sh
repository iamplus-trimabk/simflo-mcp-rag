#!/bin/bash

# Deployment script for SimFlo RAG Automated Build Pipeline
# This script sets up the build pipeline as a system service

set -e

# Configuration
SERVICE_NAME="simflo-build"
INSTALL_DIR="/opt/simflo-mcp-rag"
SERVICE_USER="simflo"
SERVICE_GROUP="simflo"
VENV_DIR="$INSTALL_DIR/venv"

echo "🚀 Deploying SimFlo RAG Build Pipeline"
echo "=" * 50

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "❌ This script must be run as root"
   exit 1
fi

# Create service user if not exists
if ! id "$SERVICE_USER" &>/dev/null; then
    echo "👤 Creating service user: $SERVICE_USER"
    useradd -r -s /bin/false -d "$INSTALL_DIR" "$SERVICE_USER"
else
    echo "👤 Service user $SERVICE_USER already exists"
fi

# Create installation directory
echo "📁 Creating installation directory: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR/rag_databases/registry_config"
mkdir -p "$INSTALL_DIR/rag_databases/extracted_data"
mkdir -p "$INSTALL_DIR/rag_databases/build_history"
mkdir -p "$INSTALL_DIR/logs"

# Copy files
echo "📋 Copying application files"
cp -r ./* "$INSTALL_DIR/"

# Set permissions
echo "🔒 Setting permissions"
chown -R "$SERVICE_USER:$SERVICE_GROUP" "$INSTALL_DIR"
chmod -R 755 "$INSTALL_DIR"
chmod +x "$INSTALL_DIR/scripts/"*.py

# Create virtual environment
echo "🐍 Creating virtual environment"
cd "$INSTALL_DIR"
sudo -u "$SERVICE_USER" python3 -m venv "$VENV_DIR"

# Install dependencies
echo "📦 Installing dependencies"
sudo -u "$SERVICE_USER" "$VENV_DIR/bin/pip" install --upgrade pip
sudo -u "$SERVICE_USER" "$VENV_DIR/bin/pip" install -r requirements.txt

# Install additional dependencies for build pipeline
sudo -u "$SERVICE_USER" "$VENV_DIR/bin/pip" install aiofiles croniter aiohttp

# Copy systemd service file
echo "⚙️ Installing systemd service"
cp deployment/simflo-build.service /etc/systemd/system/
systemctl daemon-reload

# Enable and start service
echo "🚀 Starting service"
systemctl enable "$SERVICE_NAME"
systemctl start "$SERVICE_NAME"

# Check service status
echo "📊 Checking service status"
systemctl status "$SERVICE_NAME" --no-pager

# Create log rotation
echo "📝 Setting up log rotation"
cat > /etc/logrotate.d/simflo-build << EOF
$INSTALL_DIR/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 $SERVICE_USER $SERVICE_GROUP
}
EOF

# Create monitoring script
cat > "$INSTALL_DIR/scripts/monitor_builds.py" << 'EOF'
#!/usr/bin/env python3
"""
Monitoring script for build pipeline health
"""

import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.build_service import BuildService

async def main():
    service = BuildService()

    # Get health status
    health = await service.get_service_health()

    print("📊 Build Pipeline Health Status")
    print("=" * 40)
    print(json.dumps(health, indent=2))

    # Check if service is healthy
    if health["status"] != "healthy":
        print("❌ Service is not healthy")
        sys.exit(1)

    print("✅ Service is healthy")

if __name__ == "__main__":
    asyncio.run(main())
EOF

chmod +x "$INSTALL_DIR/scripts/monitor_builds.py"

echo ""
echo "✅ Deployment completed successfully!"
echo ""
echo "📋 Management Commands:"
echo "  systemctl status $SERVICE_NAME      # Check service status"
echo "  systemctl restart $SERVICE_NAME     # Restart service"
echo "  systemctl stop $SERVICE_NAME        # Stop service"
echo "  journalctl -u $SERVICE_NAME -f     # View logs"
echo ""
echo "🔧 Manual Build Commands:"
echo "  cd $INSTALL_DIR"
echo "  sudo -u $SERVICE_USER $VENV_DIR/bin/python scripts/build_service.py --build shadcn_real"
echo "  sudo -u $SERVICE_USER $VENV_DIR/bin/python scripts/build_service.py --status"
echo ""
echo "📊 Monitoring:"
echo "  sudo -u $SERVICE_USER $VENV_DIR/bin/python scripts/monitor_builds.py"
echo ""
echo "📁 Data Directories:"
echo "  Registry configs: $INSTALL_DIR/rag_databases/registry_config"
echo "  Extracted data:   $INSTALL_DIR/rag_databases/extracted_data"
echo "  Build history:    $INSTALL_DIR/rag_databases/build_history"
echo "  Logs:             $INSTALL_DIR/logs"