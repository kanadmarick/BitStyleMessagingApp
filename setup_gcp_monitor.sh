#!/bin/bash
"""
GCP Free Tier Monitor Setup Script

This script sets up the GCP Free Tier Monitor with proper dependencies
and configuration.
"""

set -e

echo "🔧 Setting up GCP Free Tier Monitor..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Install required Python packages
echo "📦 Installing Python dependencies..."
pip3 install -r gcp_monitor_requirements.txt

# Check if gcloud is installed and configured
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud SDK is required but not installed"
    echo "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -1 > /dev/null 2>&1; then
    echo "❌ Not authenticated with gcloud"
    echo "Run: gcloud auth login"
    echo "Then: gcloud auth application-default login"
    exit 1
fi

# Get current project
PROJECT_ID=$(gcloud config get-value project 2>/dev/null || echo "")
if [ -z "$PROJECT_ID" ]; then
    echo "❌ No default project set"
    echo "Run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "✅ Project ID: $PROJECT_ID"

# Make script executable
chmod +x gcp_free_tier_monitor.py

# Create systemd service file (optional)
cat > gcp-monitor.service << EOF
[Unit]
Description=GCP Free Tier Monitor
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=$(which python3) gcp_free_tier_monitor.py --project-id $PROJECT_ID --continuous --interval 300
Restart=always
RestartSec=30
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Setup complete!"
echo ""
echo "Usage:"
echo "  # One-time check (monitoring only):"
echo "  python3 gcp_free_tier_monitor.py --project-id $PROJECT_ID --no-shutdown"
echo ""
echo "  # One-time check with emergency shutdown:"
echo "  python3 gcp_free_tier_monitor.py --project-id $PROJECT_ID"
echo ""
echo "  # Continuous monitoring every 5 minutes:"
echo "  python3 gcp_free_tier_monitor.py --project-id $PROJECT_ID --continuous"
echo ""
echo "  # Install as system service (requires sudo):"
echo "  sudo cp gcp-monitor.service /etc/systemd/system/"
echo "  sudo systemctl enable gcp-monitor.service"
echo "  sudo systemctl start gcp-monitor.service"
echo ""
echo "⚠️  WARNING: Emergency shutdown mode is enabled by default!"
echo "   Use --no-shutdown flag for monitoring only."
