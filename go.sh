#!/bin/zsh
# Porneste tot sistemul Smart Parking
set -e
cd "$(dirname "$0")"
ROOT="$(pwd)"

echo "=== Smart Parking Startup ==="

# 1. Kill stale processes
echo "[1/4] Curatare procese vechi..."
pkill -f "run_backend" 2>/dev/null || true
lsof -ti :3000 | xargs kill -9 2>/dev/null || true
lsof -ti :8090 | xargs kill -9 2>/dev/null || true
sleep 1

# 2. MQTT + PostgreSQL
echo "[2/4] Pornesc MQTT + PostgreSQL..."
brew services start mosquitto 2>/dev/null || brew services restart mosquitto 2>/dev/null || true
brew services start postgresql@16 2>/dev/null || brew services restart postgresql@16 2>/dev/null || true

# 3. Backend NestJS
echo "[3/4] Pornesc Backend NestJS pe :3000..."
cd "$ROOT/apps/api"
nohup npm run start:dev > /tmp/nest.log 2>&1 &
NEST_PID=$!
echo "    Backend PID=$NEST_PID"

# Wait for backend
echo "    Astept backend (15s)..."
for i in $(seq 1 15); do
  sleep 1
  if curl -s http://localhost:3000/health > /dev/null 2>&1; then
    echo "    Backend UP!"
    break
  fi
  echo -n "."
done
echo ""

# 4. Dashboard HTTP server
echo "[4/4] Pornesc Dashboard pe :8090..."
cd "$ROOT"
nohup python3 -m http.server 8090 > /tmp/dashboard.log 2>&1 &
echo "    Dashboard PID=$!"

echo ""
echo "=============================="
echo " GATA! Totul ruleaza:"
echo "   API:       http://localhost:3000"
echo "   Dashboard: http://localhost:8090/dashboard.html"
echo "   IP retea:  $(ipconfig getifaddr en0 2>/dev/null || echo '???')"
echo "=============================="
