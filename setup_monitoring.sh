#!/bin/bash
"""
Setup Monitoring Stack (Prometheus + Grafana)
"""

set -e

echo "🔧 Setting up Prometheus + Grafana monitoring stack..."

# Check if Docker and Docker Compose are available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is required but not installed"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is required but not installed"
    exit 1
fi

# Create monitoring directories if they don't exist
mkdir -p monitoring/prometheus/rules
mkdir -p monitoring/grafana/dashboards

# Install Python dependencies for metrics
echo "📦 Installing Python dependencies for metrics..."
pip3 install prometheus_client flask

# Create Grafana dashboards directory with proper permissions
echo "📊 Setting up Grafana dashboards..."
sudo chown -R 472:472 monitoring/grafana 2>/dev/null || true

# Create a simple alerting rule
cat > monitoring/prometheus/rules/alerts.yml << 'EOF'
groups:
  - name: ByteChat Alerts
    rules:
      - alert: HighMessageRate
        expr: rate(messages_total[5m]) > 10
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High message rate detected"
          description: "Message rate is {{ $value }} messages/sec"

      - alert: AppDown
        expr: up{job="messaging-app"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "ByteChat application is down"
          description: "The messaging application has been down for more than 1 minute"

      - alert: HighMemoryUsage
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          description: "Memory usage is above 80%"
EOF

echo "✅ Monitoring stack setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Start the monitoring stack:"
echo "   docker-compose -f docker-compose.monitoring.yml up -d"
echo ""
echo "2. Access the services:"
echo "   📊 Grafana: http://localhost:3000 (admin/admin123)"
echo "   📈 Prometheus: http://localhost:9090"
echo "   🏗️ Jenkins: http://localhost:8080"
echo "   💬 Messaging App: http://localhost:5001"
echo ""
echo "3. Import dashboards in Grafana:"
echo "   - Node Exporter Dashboard (ID: 1860)"
echo "   - Docker Container Dashboard (ID: 893)"
echo "   - Custom ByteChat Dashboard (create manually)"
echo ""
echo "4. Configure alerts (optional):"
echo "   - Set up notification channels in Grafana"
echo "   - Configure Prometheus Alertmanager"
