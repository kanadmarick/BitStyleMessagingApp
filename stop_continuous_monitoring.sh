#!/bin/bash
"""
Stop Continuous GCP Free Tier Monitoring
"""

set -e

PID_FILE="gcp_monitor.pid"

cd "$(dirname "$0")"

echo "🛑 Stopping GCP Free Tier Continuous Monitoring..."

if [ -f "$PID_FILE" ]; then
    MONITOR_PID=$(cat "$PID_FILE")
    
    if ps -p "$MONITOR_PID" > /dev/null 2>&1; then
        echo "Stopping process PID: $MONITOR_PID"
        kill "$MONITOR_PID"
        
        # Wait for process to stop
        sleep 2
        
        if ps -p "$MONITOR_PID" > /dev/null 2>&1; then
            echo "⚠️  Process still running, force killing..."
            kill -9 "$MONITOR_PID"
        fi
        
        echo "✅ Monitor stopped"
    else
        echo "⚠️  Process not running (PID: $MONITOR_PID)"
    fi
    
    rm -f "$PID_FILE"
    echo "🧹 PID file removed"
else
    echo "❌ No PID file found - monitor may not be running"
    
    # Check for any running monitors
    RUNNING_MONITORS=$(pgrep -f "gcp_free_tier_monitor_simple.py" || true)
    if [ -n "$RUNNING_MONITORS" ]; then
        echo "⚠️  Found running monitor processes:"
        ps -p $RUNNING_MONITORS
        echo ""
        echo "To kill manually:"
        echo "kill $RUNNING_MONITORS"
    fi
fi
