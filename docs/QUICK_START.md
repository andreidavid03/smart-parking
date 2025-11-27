# 🚗 Smart Parking - Quick Start Guide

## 📦 Pornire Rapidă (One-Click)

### Pornește toate serviciile:
```bash
python3 start.py
```

Acest script va:
1. ✅ Detecta automat IP-ul tău local (WiFi/Ethernet)
2. ✅ Actualiza configurația Flutter cu noul IP
3. ✅ Porni Docker containers (PostgreSQL, MQTT, Adminer)
4. ✅ Porni Backend NestJS în Terminal nou
5. ✅ Porni Flutter app în Terminal nou

### Oprește toate serviciile:
```bash
python3 stop.py
```

---

## 🎯 Ce Face Fiecare Script

### `start.py`
- **Detectare IP automată**: Nu mai trebuie să schimbi manual IP-ul când schimbi rețeaua
- **Verificări**: Verifică că Docker este pornit înainte de a începe
- **Terminal tabs separate**: Backend și Flutter rulează în tabs separate pentru debugging
- **Culori și iconițe**: Output vizual pentru a vedea ce se întâmplă
- **Error handling**: Dacă ceva nu merge, îți spune exact ce

### `stop.py`
- **Oprește Docker**: `docker-compose down` pentru toate containers
- **Oprește Backend**: Găsește și omoară procesele Node.js
- **Oprește Flutter**: Găsește și omoară procesele Flutter/Dart
- **Cleanup**: Eliberează toate porturile și resursele

---

## 🛠️ Cerințe

Asigură-te că ai instalat:
- ✅ Python 3.6+ (preinstalat pe macOS)
- ✅ Docker Desktop (trebuie să fie pornit)
- ✅ Node.js + npm
- ✅ Flutter SDK
- ✅ Xcode Command Line Tools

---

## 📱 Servicii Disponibile După Pornire

| Serviciu | URL | Descriere |
|----------|-----|-----------|
| **Backend API** | http://localhost:3000 | NestJS REST API |
| **Health Check** | http://localhost:3000/health | Verifică că backend e OK |
| **PostgreSQL** | localhost:5432 | Database |
| **Adminer** | http://localhost:8080 | Database UI |
| **MQTT Broker** | localhost:1883 | MQTT pentru senzori |
| **Flutter App** | - | iPhone Simulator |

---

## 🎮 Comenzi Utile După Pornire

### În Terminal-ul Flutter:
- `r` = Hot reload (refresh rapid UI)
- `R` = Hot restart (restart complet app)
- `q` = Quit (închide app)
- `h` = Help (alte comenzi)

### În Terminal-ul Backend:
- `Ctrl+C` = Stop server

### Docker:
```bash
# Vezi ce containere rulează
docker ps

# Vezi logs pentru PostgreSQL
docker logs infra-postgres-1

# Vezi logs pentru MQTT
docker logs infra-mqtt-1
```

---

## 🐛 Troubleshooting

### ❌ "Docker nu este pornit"
**Soluție**: Deschide Docker Desktop și așteaptă să pornească complet

### ❌ "Backend nu răspunde la http://localhost:3000/health"
**Soluție**: 
1. Verifică Terminal tab-ul cu Backend
2. Așteaptă 15-30 secunde după start
3. Rulează manual: `cd apps/api && npm run start:dev`

### ❌ "Flutter nu găsește API-ul"
**Soluție**: 
1. Verifică că IP-ul e corect în `apps/mobile/lib/services/api_service.dart`
2. Rulează din nou `python3 start.py` pentru actualizare automată

### ❌ "Port 3000 already in use"
**Soluție**:
```bash
# Găsește procesul care folosește portul 3000
lsof -i :3000

# Oprește-l
kill -9 <PID>

# Sau folosește stop.py
python3 stop.py
```

### ❌ "Simulator doesn't boot"
**Soluție**:
```bash
# Deschide manual Simulator
open -a Simulator

# Apoi rulează Flutter
cd apps/mobile && flutter run
```

---

## 🔄 Workflow Zilnic

### Dimineața (sau când începi dezvoltarea):
```bash
# Pornește tot într-un singur click
python3 start.py
```

### Seara (sau când termini):
```bash
# Oprește tot
python3 stop.py
```

### Când schimbi rețeaua WiFi:
```bash
# Oprește tot
python3 stop.py

# Pornește din nou (va detecta noul IP automat)
python3 start.py
```

---

## 📝 Structura Proiectului

```
smart-parking/
├── start.py              # 🚀 Script principal de pornire
├── stop.py               # 🛑 Script pentru oprire
├── update-ip.sh          # 📡 Script bash vechi (opțional)
├── apps/
│   ├── api/              # Backend NestJS
│   │   ├── src/
│   │   ├── prisma/
│   │   └── package.json
│   └── mobile/           # Flutter App
│       ├── lib/
│       ├── ios/
│       └── pubspec.yaml
├── infra/
│   └── docker-compose.yml  # Docker services
└── docs/
    └── QUICK_START.md    # Acest fișier
```

---

## 🎓 Pentru Prezentare / Demo

Când vrei să arăți aplicația (colegilor, profesorului, etc.):

1. **Înainte de demo** (cu 5 min):
   ```bash
   python3 start.py
   ```

2. **În timpul demo**:
   - Backend rulează automat pe fundal
   - Flutter app e deschis în Simulator
   - Poți face hot reload cu `r` pentru modificări rapide

3. **După demo**:
   ```bash
   python3 stop.py
   ```

---

## 💡 Tips & Tricks

### Verificare rapidă că totul merge:
```bash
# 1. Verifică Docker
docker ps

# 2. Verifică Backend
curl http://localhost:3000/health

# 3. Verifică PostgreSQL
docker exec -it infra-postgres-1 psql -U postgres -d smartparking -c "SELECT COUNT(*) FROM \"User\";"
```

### Resetare completă (fresh start):
```bash
# Oprește tot
python3 stop.py

# Șterge volume Docker (ATENȚIE: șterge datele din DB!)
docker-compose -f infra/docker-compose.yml down -v

# Pornește din nou
python3 start.py

# Re-seed database
cd apps/api && npx prisma migrate reset
```

---

## 📞 Help

Dacă ai probleme:
1. Verifică că ai toate cerințele instalate
2. Verifică că Docker Desktop este pornit
3. Rulează `python3 stop.py` apoi `python3 start.py`
4. Verifică logs în Terminal tabs

---

**Happy Coding! 🚀**
