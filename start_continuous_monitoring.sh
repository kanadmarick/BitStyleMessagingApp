#!/bin/bash
"""
Start Continuous GCP Free Tier Monitoring

This script starts the GCP monitor in continuous mode as a background process.
"""

set -e

PROJECT_ID="bitstyle-messaging-app"
MONITOR_SCRIPT="gcp_free_tier_monitor_simple.py"
PID_FILE="gcp_monitor.pid"
LOG_FILE="gcp_monitor_continuous.log"

cd "$(dirname "$0")"

echo "🔄 Starting GCP Free Tier Continuous Monitoring..."
echo "Project: $PROJECT_ID"
echo "Interval: 300 seconds (5 minutes)"
echo "Emergency Mode: ENABLED"
echo ""

# Check if monitor is already running
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "⚠️  Monitor is already running (PID: $OLD_PID)"
        echo "To stop it, run: kill $OLD_PID"
        exit 1
    else
        echo "🧹 Removing stale PID file"
        rm -f "$PID_FILE"
    fi
fi

# Start monitor in background
nohup python3 "$MONITOR_SCRIPT" \
    --project-id "$PROJECT_ID" \
    --continuous \
    --interval 300 \
    >> "$LOG_FILE" 2>&1 &

MONITOR_PID=$!
echo "$MONITOR_PID" > "$PID_FILE"

echo "✅ Continuous monitoring started!"
echo "   PID: $MONITOR_PID"
echo "   Log: $LOG_FILE"
echo "   PID file: $PID_FILE"
echo ""
echo "To stop monitoring:"
echo "   kill $MONITOR_PID"
echo "   rm $PID_FILE"
echo ""
echo "To view live logs:"
echo "   tail -f $LOG_FILE"
echo ""
echo "To check if running:"
echo "   ps -p $MONITOR_PID"
