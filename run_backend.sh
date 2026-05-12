#!/bin/zsh
# Auto-restarting backend runner for Smart Parking
# Usage: zsh run_backend.sh

API_DIR="$(dirname "$0")/apps/api"
LOG_FILE="/tmp/api.log"

echo "🚀 Smart Parking Backend — auto-restart enabled"
echo "   Log: $LOG_FILE"
echo "   Press Ctrl+C to stop"
echo ""

# Build first if dist is missing or stale
if [ ! -f "$API_DIR/dist/src/main.js" ]; then
  echo "⚙️  Building..."
  cd "$API_DIR" && npm run build
fi

while true; do
  echo "[$(date '+%H:%M:%S')] Starting backend..."
  cd "$API_DIR" && node dist/src/main.js 2>&1 | tee "$LOG_FILE"
  EXIT=$?
  if [ $EXIT -eq 0 ]; then
    echo "[$(date '+%H:%M:%S')] Backend exited cleanly. Stopping."
    break
  fi
  echo "[$(date '+%H:%M:%S')] Backend crashed (exit $EXIT). Restarting in 3s..."
  sleep 3
done
