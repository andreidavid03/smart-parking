# Smart Parking System — Lucrare de Licență

**Autor:** David Andrei  
**An:** 2026  
**Proiect:** Sistem inteligent de management al parcării, cu hardware IoT, aplicație mobilă și backend cloud

---

## Ce este acest proiect?

Un sistem complet de parcare inteligentă care funcționează astfel:

1. **Tu (userul) deschizi aplicația pe telefon** și te loghezi
2. **Aplcația îți generează un QR code unic**
3. **La intrarea în parcare, scanezi QR-ul** — bariera se ridică automat
4. **Sistemul îți alocă un loc liber** și îți arată pe hartă unde să mergi
5. **Senzori fizici (ESP32) și/sau camera** detectează dacă locul e ocupat sau liber
6. **La ieșire, scanezi din nou QR-ul** — bariera se ridică, sesiunea se închide
7. **Adminul poate vedea totul în timp real**: câte locuri sunt libere, cine e înăuntru, alerte de mediu

---

## Arhitectura sistemului (pe scurt)

```
┌─────────────┐     HTTP/REST      ┌──────────────────┐     PostgreSQL
│  Aplicatie  │ ◄────────────────► │   Backend NestJS  │ ◄──────────────► 🗄️ DB
│   Flutter   │                    │   (Node.js API)   │
│  (Android/  │                    └────────┬─────────┘
│    iOS)     │                             │ MQTT
└─────────────┘                    ┌────────▼─────────┐
                                   │  Mosquitto MQTT   │
                                   │     Broker        │
                                   └────────┬─────────┘
                          ┌─────────────────┼─────────────────┐
                          │                 │                  │
                   ┌──────▼──────┐  ┌───────▼──────┐  ┌──────▼──────┐
                   │    ESP32    │  │   Camera AI   │  │  Dashboard  │
                   │  (senzori,  │  │   (OpenCV +   │  │   (HTML)    │
                   │  servere,   │  │  detectare    │  │             │
                   │   LED-uri)  │  │    locuri)    │  │             │
                   └─────────────┘  └──────────────┘  └─────────────┘
```

**Pe scurt:**
- **Flutter** = aplicatia mobila (ce vede userul)
- **NestJS** = serverul care primeste requesturi si scrie in baza de date
- **PostgreSQL** = baza de date (useri, sesiuni, locuri)
- **MQTT** = protocolul prin care ESP32 si camera "vorbesc" cu serverul
- **ESP32** = microcontroller fizic cu senzori (temperatura, gaz, viteza, bariera)
- **Camera AI** = detecteaza cu OpenCV daca un loc e ocupat sau liber
- **Dashboard** = pagina HTML cu status in timp real

---

## Structura folderelor

```
smart-parking/
│
├── start.py                        ← Porneste TOT (backend + docker + camera)
├── stop.py                         ← Opreste TOT
│
├── apps/
│   ├── api/                        ← Backend-ul (NestJS + TypeScript)
│   │   ├── src/
│   │   │   ├── auth/              ← Login, signup, JWT, reset parola, email
│   │   │   ├── parking/           ← Sesiuni parcare, QR scan, config
│   │   │   ├── spots/             ← Locuri de parcare (A1-B10)
│   │   │   ├── entry/             ← Intrari/iesiri
│   │   │   ├── mqtt/              ← Comunicare cu ESP32 si camera
│   │   │   ├── email/             ← Trimitere emailuri (verificare, reset)
│   │   │   └── prisma/            ← Conexiune la baza de date
│   │   └── prisma/
│   │       ├── schema.prisma      ← Structura bazei de date
│   │       └── migrations/        ← Istoricul modificarilor DB
│   │
│   ├── mobile/                     ← Aplicatia Flutter (Android/iOS)
│   │   └── lib/
│   │       ├── screens/
│   │       │   ├── auth/          ← Login, signup, forgot password
│   │       │   ├── home/          ← Home user, home admin, QR, spots, istoric
│   │       │   ├── maps/          ← Harta Google Maps cu locuri
│   │       │   ├── payment/       ← Ecran plata
│   │       │   ├── parking/       ← Editor configuratie parcare (admin)
│   │       │   └── navigation/    ← Navigatie directionala spre loc
│   │       └── services/
│   │           ├── api_service.dart            ← Toate apelurile HTTP catre backend
│   │           └── biometric_auth_service.dart ← Face ID / Touch ID
│   │
│   ├── esp32/                      ← Cod Arduino pentru hardware
│   │   ├── smart_parking_esp32/   ← Firmware-ul principal (senzori + bariera)
│   │   ├── barrier_servo/         ← Test izolat servo bariera
│   │   ├── led_test/              ← Test LED-uri
│   │   └── i2c_scanner/           ← Utilitare depanare hardware
│   │
│   ├── camera/                     ← Detectie locuri cu camera + OpenCV
│   │   ├── detect_spots.py        ← Script principal de detectie
│   │   ├── calibrate.py           ← Calibrare zone de interes (ROI)
│   │   ├── mock_camera.py         ← Simulare camera fara hardware real
│   │   └── config.json            ← Configuratie camere si zone
│   │
│   └── dashboard/
│       └── index.html              ← Pagina web cu status parcare in timp real
│
└── infra/
    ├── docker-compose.yml          ← Porneste PostgreSQL, Adminer, MQTT, Dashboard
    └── mqtt/
        └── mosquitto.conf          ← Configuratie broker MQTT
```

---

## Tehnologii folosite

### Backend — `apps/api/`
| Ce face | Cu ce |
|--------|-------|
| Framework server | NestJS + TypeScript |
| Baza de date | PostgreSQL 16 |
| ORM (legatura cu DB) | Prisma |
| Autentificare | JWT (JSON Web Tokens) + bcrypt |
| Email | Nodemailer (SMTP Gmail) |
| Comunicare IoT | MQTT (libraria `mqtt` npm) |
| Validare date | class-validator + class-transformer |

### Aplicatie Mobila — `apps/mobile/`
| Ce face | Cu ce |
|--------|-------|
| Framework mobil | Flutter 3.x + Dart |
| Harti | Google Maps Flutter |
| QR code generare | qr_flutter |
| QR code scanare | qr_code_scanner |
| Autentificare biometrica | local_auth (Face ID / Touch ID) |
| Stocare secreta locala | flutter_secure_storage |
| Locatie GPS | geolocator + geocoding |
| Navigatie pe harta | flutter_polyline_points |
| Browser web in app | webview_flutter |

### Hardware — `apps/esp32/`
| Ce face | Cu ce |
|--------|-------|
| Microcontroller | ESP32 (WiFi + Bluetooth built-in) |
| Comunicare | MQTT over WiFi (PubSubClient) |
| Display | LCD 16x2 I2C (LiquidCrystal_I2C) |
| Temperatura + umiditate | DHT11 |
| Presiune atmosferica | BMP280 |
| Detectie gaz | MQ-4 (x2) |
| Detectie foc/flacara | Senzor flacara (x2) |
| Bariera intrare/iesire | Servo motor (ESP32Servo) |
| Indicatoare LED | FastLED (strip LED adresabil) |
| Viteza masina | 2x senzori IR LM393 (capcana viteza) |

### Camera AI — `apps/camera/`
| Ce face | Cu ce |
|--------|-------|
| Procesare imagine | OpenCV (cv2) |
| Detectie ocupare loc | Background subtraction (MOG2) |
| Comunicare cu serverul | MQTT (paho-mqtt) |
| Sursa video | Webcam / stream RTSP / video fisier |

### Infrastructura
| Serviciu | Tehnologie | Port |
|---------|-----------|------|
| Baza de date | PostgreSQL 16 (Docker) | 5432 |
| Admin DB vizual | Adminer (Docker) | 8080 |
| Broker mesaje IoT | Eclipse Mosquitto 2 (Docker) | 1883 / 9001 |
| Dashboard web | Nginx + HTML static (Docker) | 8091 |

---

## Cum pornesti proiectul

### Varianta simpla (recomandata)

```bash
# Porneste totul dintr-o singura comanda
python3 start.py

# Opreste totul
python3 stop.py
```

Scriptul `start.py` face automat:
1. Porneste Docker (PostgreSQL + MQTT + Dashboard + Adminer)
2. Ruleaza migrarile bazei de date
3. Porneste backend-ul NestJS
4. Porneste camera de detectie (daca e disponibila)

---

### Varianta manuala (pas cu pas)

#### Pasul 1 — Ce trebuie instalat inainte

```bash
node --version        # trebuie sa fie v18 sau mai nou
python3 --version     # trebuie sa fie 3.6+
flutter --version     # trebuie sa fie 3.0+
docker --version      # trebuie sa fie 20+
```

#### Pasul 2 — Porneste baza de date si serviciile (Docker)

```bash
cd infra
docker-compose up -d
```

Asta porneste:
- PostgreSQL pe portul 5432
- Adminer (interfata grafica DB) pe portul 8080
- Mosquitto MQTT pe portul 1883
- Dashboard HTML pe portul 8091

#### Pasul 3 — Configureaza backend-ul

Creeaza fisierul `apps/api/.env`:

```bash
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/smartparking"
JWT_SECRET="un-secret-lung-si-random-aici"

# Email — pentru verificare cont si reset parola
EMAIL_HOST="smtp.gmail.com"
EMAIL_PORT="587"
EMAIL_USER="emailul-tau@gmail.com"
EMAIL_PASS="parola-de-aplicatie-gmail"

# MQTT
MQTT_HOST="localhost"
MQTT_PORT="1883"
```

> **Nota Gmail:** Trebuie sa activezi "App Passwords" in contul Google (nu poti folosi parola normala).

#### Pasul 4 — Porneste backend-ul

```bash
cd apps/api
npm install
npx prisma migrate dev
npm run start:dev
```

Backend-ul porneste pe `http://localhost:3000`

#### Pasul 5 — Porneste aplicatia mobila

```bash
cd apps/mobile
flutter pub get
flutter run
```

Asigura-te ca ai un emulator pornit sau un telefon conectat prin USB.

#### Pasul 6 (optional) — Detectie locuri cu camera

```bash
cd apps/camera
pip install opencv-python paho-mqtt

# Calibreaza zonele de interes (prima data)
python3 calibrate.py

# Porneste detectia
python3 detect_spots.py --show
```

#### Pasul 7 (optional) — ESP32 Hardware

1. Deschide `apps/esp32/smart_parking_esp32/smart_parking_esp32.ino` in Arduino IDE
2. Instaleaza librariile necesare (din Library Manager):
   - `PubSubClient` by Nick O'Leary
   - `ArduinoJson` by Benoit Blanchon
   - `LiquidCrystal_I2C` by Frank de Brabander
   - `ESP32Servo` by Kevin Harrington
   - `DHT sensor library` by Adafruit
   - `FastLED`
3. Modifica credentialele WiFi si IP-ul serverului MQTT in fisier
4. Incarca codul pe ESP32

---

## Cum functioneaza (flux complet)

### Flow utilizator normal

```
1. Deschide aplicatia Flutter
2. Se inregistreaza (email + parola)
3. Verifica emailul (primeste link de verificare)
4. Se logheaza → primeste JWT token
5. Apasa "Generate QR" → apare QR-ul sau unic
6. La intrare in parcare: arata QR-ul adminului / scanerului
7. Admin/sistem scaneaza QR → bariera ESP32 se deschide
8. Sistemul aloca un loc liber (ex: A3)
9. Userul vede pe harta unde e locul A3
10. Parcheaza masina
11. Camera / senzor ESP32 detecteaza masina → locul devine "ocupat" (rosu)
12. La plecare: arata QR-ul din nou → bariera se deschide → sesiunea se inchide
```

### Flow admin

```
1. Logat cu cont de admin
2. Vede toate locurile in timp real (verde = liber, rosu = ocupat)
3. Poate scana QR-uri de utilizatori
4. Vede istoricul tuturor sesiunilor
5. Primeste alerte de mediu de la ESP32 (temperatura, gaz, foc)
6. Poate configura harta parcarii (adauga/sterge locuri)
```

---

## API Endpoints (ce poate face serverul)

### Autentificare
| Metoda | URL | Ce face |
|--------|-----|---------|
| POST | `/auth/signup` | Inregistrare utilizator nou |
| POST | `/auth/login` | Login, returneaza JWT |
| GET | `/auth/verify-email?token=xxx` | Verifica emailul |
| POST | `/auth/forgot-password` | Trimite email de reset parola |
| POST | `/auth/reset-password` | Seteaza parola noua |
| POST | `/auth/update-car-color` | Actualizeaza culoarea masinii |
| POST | `/auth/set-preferred-spot` | Seteaza locul preferat (A1-B10) |
| POST | `/auth/profile` | Returneaza datele profilului |

### Parcare
| Metoda | URL | Ce face |
|--------|-----|---------|
| POST | `/parking/generate-qr` | Genereaza QR code unic pentru user |
| POST | `/parking/scan-qr` | Scaneaza QR (check-in sau check-out) |
| POST | `/parking/current-session` | Returneaza sesiunea activa |

### Locuri
| Metoda | URL | Ce face |
|--------|-----|---------|
| GET | `/spots` | Lista tuturor locurilor cu status |
| GET | `/spots/:id` | Detalii loc specific |

### Health
| Metoda | URL | Ce face |
|--------|-----|---------|
| GET | `/health` | Verifica daca serverul e pornit |

---

## Topicuri MQTT (cum comunica ESP32 cu serverul)

| Topic | Directie | Ce contine |
|-------|----------|-----------|
| `parking/commands` | Server → ESP32 | `{"command": "OPEN_ENTRY", "spot": "A1"}` |
| `parking/commands` | Server → ESP32 | `{"command": "OPEN_EXIT"}` |
| `parking/environment` | ESP32 → Server | Temperatura, umiditate, presiune, gaz, foc |
| `parking/speed` | ESP32 → Server | Viteza masinii la intrare (km/h) |
| `parking/diagnostics` | ESP32 → Server | Toate citirile brute (debug) |
| `parking/sensor/<LOC>` | Camera → Server | `{"status": "occupied"}` sau `{"status": "available"}` |

---

## Baza de date (schema simplificata)

```
User
├── id (UUID)
├── email (unic)
├── password (hash bcrypt)
├── role ("user" sau "admin")
├── emailVerified (true/false)
├── carColor (culoarea masinii — optional)
├── preferredSpot (ex: "A3" — optional)
└── qrCode (codul QR unic — optional)

Spot
├── id (UUID)
├── name (ex: "A1", "B5")
├── status ("available" sau "occupied")
├── latitude / longitude (coordonate pe harta)
└── sensorId (ID senzor fizic asociat — optional)

Session
├── id (UUID)
├── userId (cine a parcat)
├── spotId (unde a parcat)
├── startTime (cand a intrat)
└── endTime (cand a plecat — null daca inca e acolo)

ParkingConfig
├── id
├── name (numele parcarii)
├── totalSpots
├── address
└── coordinates
```

---

## Porturi si servicii — sumar rapid

| Serviciu | Port | Link direct |
|---------|------|------------|
| Backend API | 3000 | http://localhost:3000 |
| Health check | 3000 | http://localhost:3000/health |
| PostgreSQL | 5432 | (accesat intern de backend) |
| Adminer (DB vizual) | 8080 | http://localhost:8080 |
| Dashboard parcare | 8091 | http://localhost:8091 |
| MQTT TCP | 1883 | (folosit de ESP32 si camera) |
| MQTT WebSocket | 9001 | (folosit de dashboard web) |

---

## Depanare probleme frecvente

**Backend nu porneste:**
```bash
# Verifica daca Docker e pornit
docker ps

# Verifica daca baza de date e accesibila
cd apps/api && npx prisma migrate status
```

**Aplicatia mobila nu se conecteaza la backend:**
- Daca rulezi pe emulator Android: schimba `localhost` cu `10.0.2.2` in `api_service.dart`
- Daca rulezi pe telefon real: foloseste IP-ul local al calculatorului (ex: `192.168.1.x`)

**ESP32 nu se conecteaza la MQTT:**
- Verifica ca ESP32 si calculatorul sunt pe aceeasi retea WiFi
- Verifica IP-ul brokerului MQTT in fisierul `.ino` (variabila `MQTT_BROKER`)
- Verifica ca Docker e pornit si Mosquitto ruleaza: `docker ps | grep mosquitto`

**Camera nu detecteaza corect locurile:**
```bash
# Recalibreaza zonele de interes
cd apps/camera
python3 calibrate.py
# Salveaza output-ul in config.json
```

**Email-urile nu se trimit:**
- Activeaza "2-Step Verification" in Gmail
- Genereaza un "App Password" in setarile Google si foloseste-l in `.env`

---

## Rulare teste

```bash
# Backend
cd apps/api
npm run test          # teste unitare
npm run test:e2e      # teste end-to-end
npm run test:cov      # acoperire cod

# Mobil
cd apps/mobile
flutter test
```

---

## Autor

**David Andrei**  
Lucrare de Licenta — 2026  
Sistem inteligent de management al parcarii cu IoT, AI si aplicatie mobila
