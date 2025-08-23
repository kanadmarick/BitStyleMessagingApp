#!/bin/bash
"""
Start Complete Monitoring Stack
"""

set -e

echo "🚀 Starting ByteChat Monitoring Stack..."

# Check if setup was run
if [ ! -f "monitoring/prometheus/prometheus.yml" ]; then
    echo "⚠️  Monitoring not set up yet. Running setup..."
    ./setup_monitoring.sh
fi

# Start the monitoring stack
echo "📊 Starting Prometheus + Grafana stack..."
docker-compose -f docker-compose.monitoring.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "🔍 Checking service health..."

# Check Prometheus
if curl -s http://localhost:9090/-/healthy > /dev/null; then
    echo "✅ Prometheus is running"
else
    echo "❌ Prometheus failed to start"
fi

# Check Grafana
if curl -s http://localhost:3000/api/health > /dev/null; then
    echo "✅ Grafana is running"
else
    echo "❌ Grafana failed to start"
fi

# Check if messaging app is built and ready
if [ -f "Dockerfile" ]; then
    echo "📱 Messaging app container ready"
else
    echo "⚠️  No Dockerfile found - messaging app may not be containerized yet"
fi

echo ""
echo "🎉 Monitoring Stack Started Successfully!"
echo ""
echo "📋 Access your services:"
echo "   📊 Grafana Dashboard: http://localhost:3000"
echo "      Username: admin"
echo "      Password: admin123"
echo ""
echo "   📈 Prometheus: http://localhost:9090"
echo "   🏗️ Jenkins: http://localhost:8080"
echo "   💬 Messaging App: http://localhost:5001"
echo "   📊 Node Metrics: http://localhost:9100"
echo "   🐳 Container Metrics: http://localhost:8081"
echo ""
echo "📊 To view logs:"
echo "   docker-compose -f docker-compose.monitoring.yml logs -f"
echo ""
echo "🛑 To stop the stack:"
echo "   docker-compose -f docker-compose.monitoring.yml down"
