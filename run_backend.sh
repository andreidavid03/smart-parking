#!/bin/zsh
# Auto-restarting backend runner for Smart Parking
# Usage: zsh run_backend.sh  (run from project root)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
API_DIR="$SCRIPT_DIR/apps/api"
LOG_FILE="/tmp/api.log"

echo "🚀 Smart Parking Backend — auto-restart enabled"
echo "   API dir: $API_DIR"
echo "   Log: $LOG_FILE"
echo "   Press Ctrl+C to stop"
echo ""

while true; do
  echo "[$(date '+%H:%M:%S')] Starting backend..."
  cd "$API_DIR" && npm run start:dev 2>&1 | tee "$LOG_FILE"
  EXIT=$?
  if [ $EXIT -eq 0 ]; then
    echo "[$(date '+%H:%M:%S')] Backend exited cleanly. Stopping."
    break
  fi
  echo "[$(date '+%H:%M:%S')] Backend crashed (exit $EXIT). Restarting in 3s..."
  sleep 3
done
