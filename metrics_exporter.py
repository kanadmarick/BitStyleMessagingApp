#!/usr/bin/env python3
"""
Prometheus Metrics Endpoint for ByteChat Messaging App
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from flask import Response
import time
import sqlite3
import os

# Prometheus metrics
message_count = Counter('messages_total', 'Total number of messages sent')
active_users = Gauge('active_users', 'Number of currently active users')
response_time = Histogram('http_request_duration_seconds', 'HTTP request duration in seconds')
db_size = Gauge('database_size_bytes', 'Size of messages database in bytes')
uptime = Gauge('app_uptime_seconds', 'Application uptime in seconds')

# App start time for uptime calculation
app_start_time = time.time()

def get_database_metrics():
    """Get database-related metrics"""
    try:
        db_path = 'messages.db'
        if os.path.exists(db_path):
            # Database file size
            db_size.set(os.path.getsize(db_path))
            
            # Message count from database
            with sqlite3.connect(db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM messages")
                count = cursor.fetchone()[0]
                message_count._value._value = count
        else:
            db_size.set(0)
            
    except Exception as e:
        print(f"Error collecting database metrics: {e}")

def get_app_metrics():
    """Get application-level metrics"""
    # Update uptime
    current_uptime = time.time() - app_start_time
    uptime.set(current_uptime)

def metrics_endpoint():
    """Prometheus metrics endpoint"""
    # Collect latest metrics
    get_database_metrics()
    get_app_metrics()
    
    # Generate Prometheus format response
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

# Export metrics functions for use in main app
__all__ = ['metrics_endpoint', 'message_count', 'active_users', 'response_time']
