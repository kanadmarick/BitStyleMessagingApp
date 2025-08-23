# ByteChat Monitoring & Observability Stack

## Overview

ByteChat features a comprehensive monitoring stack built with industry-standard tools to provide full observability into application performance, system health, and user behavior.

## Architecture

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Flask App     │───▶│ Prometheus   │───▶│    Grafana      │
│  (Port 5003)    │    │ (Port 9090)  │    │  (Port 3000)    │
│                 │    │              │    │                 │
│ /metrics        │    │ Data Storage │    │ Dashboards      │
│ /health         │    │ Alerting     │    │ Visualization   │
└─────────────────┘    └──────────────┘    └─────────────────┘
          │                      ▲
          │                      │
          ▼                      │
┌─────────────────┐              │
│   SQLite DB     │              │
│ messages.db     │──────────────┘
│                 │
│ Message Storage │
│ Usage Analytics │
└─────────────────┘

        Additional Data Sources:
┌─────────────────┐    ┌─────────────────┐
│ Node Exporter   │    │    cAdvisor     │
│ (Port 9100)     │    │  (Port 8081)    │
│                 │    │                 │
│ System Metrics  │    │Container Metrics│
└─────────────────┘    └─────────────────┘
```

## Components

### 1. Prometheus (Port 9090)
**Purpose**: Metrics collection, storage, and querying

**Features**:
- Scrapes metrics every 30 seconds from all targets
- Stores time-series data with configurable retention
- Provides PromQL query language for data analysis
- Built-in alerting capabilities

**Targets**:
- Flask Application: `host.docker.internal:5003/metrics`
- Node Exporter: `node_exporter:9100/metrics`
- cAdvisor: `cadvisor:8080/metrics`
- Jenkins: `jenkins:8080/prometheus`

### 2. Grafana (Port 3000)
**Purpose**: Visualization and dashboarding

**Default Login**: `admin/admin`

**Features**:
- Real-time dashboard creation
- Alert notifications
- Data exploration tools
- Custom panel types

**Recommended Dashboards**:
- Application Overview (messages, users, uptime)
- System Resources (CPU, memory, disk)
- Container Metrics (Docker performance)
- Business Metrics (message patterns, peak hours)

### 3. Flask Application Metrics

#### Custom Metrics Exposed

| Metric Name | Type | Description |
|-------------|------|-------------|
| `messages_total` | Counter | Total number of messages sent |
| `active_users` | Gauge | Currently connected users |
| `database_size_bytes` | Gauge | SQLite database file size |
| `app_uptime_seconds` | Gauge | Application runtime |
| `http_request_duration_seconds` | Histogram | Response time distribution |

#### Health Endpoints

- **`/health`**: Application health status
- **`/metrics`**: Prometheus metrics endpoint
- **`/history`**: Message history API

### 4. Node Exporter (Port 9100)
**Purpose**: System-level metrics

**Metrics Include**:
- CPU usage and load average
- Memory utilization
- Disk I/O and space usage
- Network interface statistics
- System processes and file descriptors

### 5. cAdvisor (Port 8081)
**Purpose**: Container performance metrics

**Metrics Include**:
- Container CPU and memory usage
- Network and disk I/O per container
- Container filesystem usage
- Performance characteristics

## Quick Start

### 1. Start Complete Stack
```bash
# Make scripts executable
chmod +x setup_monitoring.sh start_monitoring_stack.sh

# Setup monitoring (first time only)
./setup_monitoring.sh

# Start the complete stack
./start_monitoring_stack.sh
```

### 2. Verify Services
```bash
# Check all containers are running
docker ps

# Test Prometheus
curl http://localhost:9090/api/v1/targets

# Test Flask metrics
curl http://localhost:5003/metrics

# Test application health
curl http://localhost:5003/health
```

### 3. Access Dashboards
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Application**: http://localhost:5003

## Custom Queries

### Application Performance
```promql
# Messages per minute
rate(messages_total[5m]) * 60

# Average response time
rate(http_request_duration_seconds_sum[5m]) / 
rate(http_request_duration_seconds_count[5m])

# Database growth rate
rate(database_size_bytes[1h])
```

### System Health
```promql
# CPU usage percentage
100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory usage percentage
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# Disk usage percentage
(1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100
```

### Container Metrics
```promql
# Container memory usage
container_memory_usage_bytes{name=~".+"}

# Container CPU usage
rate(container_cpu_usage_seconds_total{name=~".+"}[5m])
```

## Alerting Rules

### Critical Alerts
- Application down (up == 0)
- High memory usage (> 90%)
- Disk space low (< 10%)
- High response time (> 5s)

### Warning Alerts
- Memory usage (> 75%)
- CPU usage (> 80%)
- Message rate spike (> 100/min)

## Troubleshooting

### Common Issues

1. **Metrics not appearing**
   - Check if Flask app is running on correct port
   - Verify Prometheus scraping configuration
   - Check Docker network connectivity

2. **Grafana not showing data**
   - Verify Prometheus data source configuration
   - Check query syntax in panels
   - Ensure time range is appropriate

3. **Container metrics missing**
   - Verify cAdvisor has access to Docker socket
   - Check container permissions
   - Restart cAdvisor container

### Debug Commands
```bash
# Check Prometheus targets
curl -s http://localhost:9090/api/v1/targets | jq .

# Test custom metrics
curl -s http://localhost:9090/api/v1/query?query=messages_total

# Check container logs
docker logs prometheus
docker logs grafana
docker logs messaging-app
```

## Production Considerations

### Security
- Change default Grafana password
- Enable HTTPS for external access
- Configure authentication for Prometheus
- Set up network policies

### Performance
- Configure appropriate retention periods
- Set up external storage for long-term data
- Monitor resource usage of monitoring stack
- Implement metric filtering

### Backup
- Export Grafana dashboards
- Backup Prometheus configuration
- Document custom alert rules
- Store notification channel configs

## Integration with CI/CD

The monitoring stack integrates with Jenkins for:
- Build metric collection
- Deployment monitoring
- Performance regression detection
- Automated alerting on failures

See `jenkins_gcp_monitor.py` for Jenkins-specific monitoring implementation.
