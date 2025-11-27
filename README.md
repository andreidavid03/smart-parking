# 🚗 Smart Parking System

> Sistem inteligent de parcare cu QR code, GPS navigation, și monitorizare în timp real.

## 📋 Descriere

Aplicație full-stack pentru gestionarea unui parking inteligent. Permite utilizatorilor să:
- 📱 Se autentifice cu biometric (Face ID / Touch ID)
- 🔍 Scaneze QR code pentru intrare/ieșire
- 🗺️ Vizualizeze harta parcării în timp real
- 🧭 Primească navigație GPS până la locul alocat
- ⭐ Seteze preferințe pentru locuri de parcare
- 📊 Vadă istoric complet sesiuni

Adminii pot:
- 🎯 Scana QR-uri utilizatori
- 📍 Vedea toate locurile ocupate/libere
- 📈 Monitorizeze activitatea din parcare

## 🚀 Quick Start

### Pornește TOTUL într-o singură comandă:
```bash
python3 start.py
```

### Oprește TOTUL:
```bash
python3 stop.py
```

Da, chiar e atât de simplu! 🎉

## 📚 Documentație Completă

- 📖 [Quick Start Guide](docs/QUICK_START.md) - Ghid complet de pornire
- ⚡ [Shell Aliases](docs/ALIASES.md) - Comenzi rapide și shortcuts

## 🛠️ Tech Stack

### Backend (NestJS)
- **Framework**: NestJS + TypeScript
- **Database**: PostgreSQL cu Prisma ORM
- **Auth**: JWT + bcrypt + Email verification
- **Email**: Nodemailer
- **MQTT**: Eclipse Mosquitto (pentru senzori IoT)

### Frontend (Flutter)
- **Framework**: Flutter 3.x + Dart
- **Maps**: Google Maps Flutter
- **Auth**: Biometric (Face ID / Touch ID)
- **QR**: QR Flutter + Mobile Scanner
- **State**: StatefulWidget + setState

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Database Admin**: Adminer
- **Message Broker**: MQTT Broker

## 📁 Structura Proiectului

```
smart-parking/
├── start.py                    # 🚀 Script pornire automată
├── stop.py                     # 🛑 Script oprire automată
├── apps/
│   ├── api/                    # Backend NestJS
│   │   ├── src/
│   │   │   ├── auth/          # Autentificare & profil
│   │   │   ├── parking/       # Sesiuni parcare
│   │   │   ├── spots/         # Management locuri
│   │   │   ├── entry/         # Intrări/ieșiri
│   │   │   ├── email/         # Email service
│   │   │   └── prisma/        # Database client
│   │   └── prisma/
│   │       ├── schema.prisma  # Database schema
│   │       └── migrations/    # Database migrations
│   └── mobile/                # Flutter App
│       ├── lib/
│       │   ├── screens/
│       │   │   ├── auth/      # Login, signup, forgot password
│       │   │   ├── home/      # Home screens (user/admin)
│       │   │   └── maps/      # Google Maps integration
│       │   └── services/
│       │       ├── api_service.dart           # HTTP client
│       │       └── biometric_auth_service.dart # Biometric
│       └── ios/               # iOS specific
├── infra/
│   ├── docker-compose.yml     # Docker services
│   └── mqtt/
│       └── mosquitto.conf     # MQTT config
└── docs/
    ├── QUICK_START.md         # Ghid complet
    └── ALIASES.md             # Shell shortcuts
```

## 🎯 Features Implementate

### ✅ Autentificare & Profil
- [x] Signup cu email verification
- [x] Login cu JWT
- [x] Forgot password cu reset token
- [x] Biometric login (Face ID / Touch ID)
- [x] Profile screen cu tabs
- [x] Car color selection
- [x] Preferred spot selection (A1-B10)

### ✅ Parking Management
- [x] Generate QR code unic per user
- [x] QR code scan (admin)
- [x] Check-in/check-out automat
- [x] Session tracking
- [x] Real-time spots availability

### ✅ Maps & Navigation
- [x] Google Maps integration
- [x] 20 parking spots (A1-A10, B1-B10)
- [x] Real-time marker colors (green/red)
- [x] Tap marker for details
- [x] Legend & counter
- [ ] GPS navigation to assigned spot (în lucru)

### 🔄 În Dezvoltare
- [ ] Navigation screen cu polyline
- [ ] BYPASS buttons pentru simulare hardware
- [ ] WebSockets pentru real-time updates
- [ ] Push notifications (Firebase)
- [ ] Payment integration (Revolut/Stripe)

## 🔧 Setup Manual (dacă nu vrei script-ul)

### Prerequisites
```bash
# Verifică versiunile
node --version        # v18+
python3 --version     # 3.6+
flutter --version     # 3.0+
docker --version      # 20+
```

### Backend
```bash
cd apps/api
npm install
npx prisma migrate dev
npm run start:dev
```

### Frontend
```bash
cd apps/mobile
flutter pub get
flutter run
```

### Docker
```bash
cd infra
docker-compose up -d
```

## 🌐 Servicii & Porturi

| Serviciu | Port | URL |
|----------|------|-----|
| Backend API | 3000 | http://localhost:3000 |
| Health Check | 3000 | http://localhost:3000/health |
| PostgreSQL | 5432 | localhost:5432 |
| Adminer | 8080 | http://localhost:8080 |
| MQTT | 1883 | localhost:1883 |
| MQTT WebSocket | 9001 | localhost:9001 |

## 📱 Database Schema

### User Model
```prisma
model User {
  id                   String    @id @default(uuid())
  email                String    @unique
  password             String
  role                 String    @default("user")
  emailVerified        Boolean   @default(false)
  carColor             String?
  preferredSpot        String?   # A1-B10
  qrCode               String?   @unique
  sessions             Session[]
}
```

### Spot Model
```prisma
model Spot {
  id        String    @id @default(uuid())
  name      String    # A1, A2, ..., B10
  status    String    @default("available")
  sessions  Session[]
}
```

### Session Model
```prisma
model Session {
  id        String   @id @default(uuid())
  userId    String
  spotId    String
  startTime DateTime @default(now())
  endTime   DateTime?
  user      User     @relation(fields: [userId])
  spot      Spot     @relation(fields: [spotId])
}
```

## 🔑 Environment Variables

Creează `.env` în `apps/api/`:

```bash
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/smartparking"
JWT_SECRET="your-secret-key"

# Email (Nodemailer)
EMAIL_HOST="smtp.gmail.com"
EMAIL_PORT="587"
EMAIL_USER="your-email@gmail.com"
EMAIL_PASS="your-app-password"

# Google Maps (doar pentru production)
GOOGLE_MAPS_API_KEY="your-api-key"
```

## 📊 API Endpoints

### Auth
- `POST /auth/signup` - Register new user
- `POST /auth/login` - Login
- `GET /auth/verify-email?token=xxx` - Verify email
- `POST /auth/forgot-password` - Request reset
- `POST /auth/reset-password` - Reset password
- `POST /auth/update-car-color` - Update car color
- `POST /auth/set-preferred-spot` - Set preferred spot
- `POST /auth/profile` - Get user profile

### Parking
- `POST /parking/generate-qr` - Generate QR code
- `POST /parking/scan-qr` - Scan QR (check-in/out)
- `POST /parking/current-session` - Get active session

### Spots
- `GET /spots` - Get all spots with status

## 🧪 Testing

### Backend Tests
```bash
cd apps/api
npm run test           # Unit tests
npm run test:e2e       # E2E tests
npm run test:cov       # Coverage
```

### Flutter Tests
```bash
cd apps/mobile
flutter test
flutter test --coverage
```

## 🐛 Troubleshooting

Vezi [Quick Start Guide](docs/QUICK_START.md#-troubleshooting) pentru soluții comune.

## 📝 Changelog

### v1.0.0 (Current)
- ✅ Complete auth system
- ✅ Profile management with tabs
- ✅ Google Maps integration
- ✅ QR code generation & scanning
- ✅ Session tracking
- ✅ One-click startup scripts

### v1.1.0 (Planned)
- 🔄 GPS navigation
- 🔄 Hardware simulation (BYPASS buttons)
- 🔄 Push notifications
- 🔄 Payment integration

## 👨‍💻 Author

**David Andrei**
- University: [Your University Name]
- Project: Bachelor's Thesis - Smart Parking System
- Year: 2025

## 📄 License

This is a university thesis project.

---

## 🎓 Pentru Prezentare

Când vrei să prezinți proiectul:

1. **Pornește totul**:
   ```bash
   python3 start.py
   ```

2. **Demo flow**:
   - Login cu biometric
   - Vezi QR code-ul tău
   - Navighează pe hartă (Map tab)
   - Schimbă preferred spot (Profile → Spot Preference)
   - Admin: scanează QR, vezi toate sesiunile

3. **Oprește după demo**:
   ```bash
   python3 stop.py
   ```

---

**Made with ❤️ for my Bachelor's Thesis**

🚀 **Quick Start**: `python3 start.py`  
📖 **Docs**: `docs/QUICK_START.md`  
🛑 **Stop**: `python3 stop.py`
