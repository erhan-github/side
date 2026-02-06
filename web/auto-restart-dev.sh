#!/bin/bash

# Auto-restart Next.js dev server when memory exceeds threshold
# Usage: ./auto-restart-dev.sh

MEMORY_THRESHOLD_MB=3072  # 3GB threshold
CHECK_INTERVAL=300        # Check every 5 minutes

echo "🚀 Starting Next.js dev server with auto-restart on high memory usage..."
echo "Memory threshold: ${MEMORY_THRESHOLD_MB}MB"
echo "Check interval: ${CHECK_INTERVAL}s"
echo ""

while true; do
  # Start the dev server in background
  npm run dev &
  DEV_PID=$!
  
  echo "✅ Dev server started (PID: $DEV_PID)"
  
  # Monitor memory usage
  while kill -0 $DEV_PID 2>/dev/null; do
    sleep $CHECK_INTERVAL
    
    # Get memory usage in MB (RSS)
    MEMORY_MB=$(ps -o rss= -p $DEV_PID 2>/dev/null | awk '{print int($1/1024)}')
    
    if [ -z "$MEMORY_MB" ]; then
      echo "⚠️  Process $DEV_PID not found, restarting..."
      break
    fi
    
    echo "📊 Memory usage: ${MEMORY_MB}MB / ${MEMORY_THRESHOLD_MB}MB"
    
    if [ "$MEMORY_MB" -gt "$MEMORY_THRESHOLD_MB" ]; then
      echo "🔴 Memory threshold exceeded! Restarting dev server..."
      kill $DEV_PID 2>/dev/null
      sleep 2
      break
    fi
  done
  
  echo "♻️  Restarting in 3 seconds..."
  sleep 3
done
