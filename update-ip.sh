#!/bin/bash

# Script pentru actualizare automată IP în Flutter
# Detectează IP-ul curent și îl actualizează în api_service.dart

# Detectează IP-ul
NEW_IP=$(ipconfig getifaddr en0)

if [ -z "$NEW_IP" ]; then
    echo "❌ Nu am putut detecta IP-ul. Verifică conexiunea WiFi."
    exit 1
fi

echo "🔍 IP detectat: $NEW_IP"

# Calea către fișierul Flutter
API_SERVICE_FILE="apps/mobile/lib/services/api_service.dart"

# Verifică dacă fișierul există
if [ ! -f "$API_SERVICE_FILE" ]; then
    echo "❌ Fișierul $API_SERVICE_FILE nu a fost găsit!"
    exit 1
fi

# Actualizează IP-ul în fișier
# Caută linia cu baseUrl și o înlocuiește
sed -i.bak "s|static const String baseUrl = 'http://[0-9.]*:3000'|static const String baseUrl = 'http://$NEW_IP:3000'|g" "$API_SERVICE_FILE"

echo "✅ IP actualizat la $NEW_IP în $API_SERVICE_FILE"
echo ""
echo "Pornesc serverele..."
echo ""

# Oprește procesele vechi
killall -9 node flutter dart 2>/dev/null || true

# Pornește backend în background
echo "🚀 Pornesc backend..."
cd apps/api
npm run start:dev > /dev/null 2>&1 &
BACKEND_PID=$!
cd ../..

# Așteaptă backend să pornească
sleep 5

# Verifică dacă backend rulează
if curl -s http://$NEW_IP:3000/health > /dev/null; then
    echo "✅ Backend pornit cu succes pe http://$NEW_IP:3000"
else
    echo "⚠️  Backend pornit dar nu răspunde încă..."
fi

echo ""
echo "🚀 Pornesc Flutter..."
echo "   (Apasă Ctrl+C pentru a opri)"
echo ""

# Pornește Flutter
cd apps/mobile
flutter run

# Cleanup la exit
trap "killall -9 node flutter dart 2>/dev/null; exit" INT TERM
