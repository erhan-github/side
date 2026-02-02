#!/bin/bash

# Sidelith Flight Recorder
# Ensures all stderr/stdout is captured for the Log Scavenger.

mkdir -p .side/logs
LOG_FILE=".side/logs/server.log"

echo "🚀 [STARTUP]: Starting Sidelith Server..."
echo "📂 [LOGS]: Piping output to $LOG_FILE"

# Rotate logs (keep last 5)
if [ -f "$LOG_FILE" ]; then
    mv "$LOG_FILE" "$LOG_FILE.old"
fi

# Run Server with piping
# 2>&1 redirects stderr to stdout
python3 scripts/run_server.py > "$LOG_FILE" 2>&1 &
PID=$!

echo $PID > .side/server.pid
echo "✅ [STARTED]: Server running with PID $PID"
echo "tail -f $LOG_FILE to watch live."
