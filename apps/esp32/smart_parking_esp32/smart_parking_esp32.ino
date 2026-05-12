/**
 * Smart Parking – ESP32 Hardware Controller
 * ==========================================
 * Libraries required (install via Arduino Library Manager):
 *   - PubSubClient         by Nick O'Leary  (MQTT)
 *   - ArduinoJson          by Benoit Blanchon (v6 or v7)
 *   - LiquidCrystal_I2C    by Frank de Brabander
 *   - ESP32Servo           by Kevin Harrington
 *   - DHT sensor library   by Adafruit
 *   - Adafruit BMP280 Library by Adafruit
 *   - Adafruit Unified Sensor by Adafruit
 *
 * Subscribed topic:  parking/commands
 * Expected payload:  {"command": "OPEN_ENTRY", "spot": "A1"}
 *                 or {"command": "OPEN_EXIT"}
 *
 * Published topics:
 *   parking/speed            → JSON {speed_kmh, elapsed_ms}          (IR speed trap)
 *   parking/environment      → JSON {temp, humidity, pressure, bmp_temp,
 *                                    gas1, gas2, flame1, flame2}        (every 5s)
 *   parking/diagnostics      → JSON with all raw pin readings           (every 2s)
 *
 * MQTT commands:
 *   parking/commands  {"command":"OPEN_ENTRY","spot":"A1"}  → entry servo
 *   parking/commands  {"command":"OPEN_EXIT","spot":"A1"}   → exit servo
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <ESP32Servo.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <FastLED.h>
#include <DHT.h>
// BMP280 inlocuit cu mock (senzor absent din proiect)

// ─── Configuration ────────────────────────────────────────────────────────────
// Replace with your actual Wi-Fi credentials and the local IP of your PC.
const char* WIFI_SSID      = "thezuni-1";
const char* WIFI_PASSWORD  = "0744804859";
const char* MQTT_BROKER   = "192.168.1.210";     // PC local IP (runs Mosquitto)
const int   MQTT_PORT      = 1883;
const char* MQTT_CLIENT_ID = "smart-parking-esp32";

const char* TOPIC_COMMANDS   = "parking/commands";
const char* TOPIC_ENV        = "parking/environment";
const char* TOPIC_SPEED      = "parking/speed";
const char* TOPIC_DIAG       = "parking/diagnostics";

// ─── Sensor pins ─────────────────────────────────────────────────────────────
#define DHT_PIN      4    // GPIO4  — DHT11 data pin
#define DHT_TYPE     DHT11

// IR speed trap — mount these two sensors in the entry lane, ~10 cm apart
#define IR_PIN_1     34   // GPIO34 — IR LM393 #1 (first beam, input-only)
#define IR_PIN_2     35   // GPIO35 — IR LM393 #2 (second beam, input-only)
#define IR_DISTANCE_CM 10.0  // measured physical gap between the two sensors

// MQ-4 gas sensors — ADC1 pins, safe to use with WiFi active
#define MQ4_PIN_1    32   // GPIO32 — MQ-4 left side
#define MQ4_PIN_2    33   // GPIO33 — MQ-4 right side

// Flame sensors — digital only
#define FLAME_PIN_1  25   // GPIO25 — Flame sensor left side  (LOW = flame)
#define FLAME_PIN_2  26   // GPIO26 — Flame sensor right side (LOW = flame)

// Publish environment data every N milliseconds
#define ENV_PUBLISH_INTERVAL_MS  5000
#define DIAG_PUBLISH_INTERVAL_MS 2000

// ─── Servo pins ───────────────────────────────────────────────────────────────
const int SERVO_ENTRY_PIN   = 18;   // GPIO18 — entry barrier servo signal
const int SERVO_EXIT_PIN    = 19;   // GPIO19 — exit barrier servo signal
const int SERVO_OPEN        = 90;   // degrees — open position
const int SERVO_CLOSED      = 0;    // degrees — closed position
const int OPEN_DELAY_MS     = 4000; // ms barrier stays open

// WS2812B LED strip
#define LED_PIN      5    // D5 — data line to WS2812B DIN (use 330Ω resistor in series)
#define NUM_LEDS     15   // 5 columns × 3 LEDs per column (A1-A5, B1-B5)
#define LEDS_PER_SPOT 3   // physical LED count illuminating each parking bay
CRGB leds[NUM_LEDS];

// LCD: 0x27 is the most common I2C address; try 0x3F if display is blank
LiquidCrystal_I2C lcd(0x27, 16, 2);
// ─────────────────────────────────────────────────────────────────────────────

WiFiClient      wifiClient;
PubSubClient    mqttClient(wifiClient);
Servo           entryServo;
// exitServo removed — hardware burned, using entryServo for both barriers
DHT             dht(DHT_PIN, DHT_TYPE);
// Adafruit_BMP280 bmp; -- inlocuit cu mock

// Per-column spot state (index 0=col1 … 4=col5) — A1-A5, B1-B5
// Priority: occupied > reserved > free
bool occupiedA[5]  = {false};
bool occupiedB[5]  = {false};
bool reservedA[5]  = {false};
bool reservedB[5]  = {false};

// ─── Speed trap state ────────────────────────────────────────────────────────
bool          ir1Triggered   = false;   // beam 1 currently broken
unsigned long ir1Time        = 0;       // millis when beam 1 first broke
bool          speedArmed     = false;   // waiting for beam 2 after beam 1

// Millis timestamp of last environment publish
unsigned long lastEnvPublish  = 0;
unsigned long lastDiagPublish = 0;

// ─── Forward declarations ─────────────────────────────────────────────────────
void connectWiFi();
void connectMQTT();
void onMqttMessage(char* topic, byte* payload, unsigned int length);
void openEntryBarrier();
int  spotToColumn(String spot);
void markSpotOccupied(String spot);
void markSpotFree(String spot);
void markSpotReserved(String spot);
void markSpotUnreserved(String spot);
void lcdShow(const char* line1, const char* line2 = "");
void publishEnvironment();
void publishDiagnostics();
void checkSpeedTrap();
void openEntryBarrier();
void openExitBarrier();

// ─── Setup ────────────────────────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println("\n=== Smart Parking ESP32 Controller ===");

  lcd.init();
  lcd.backlight();
  lcdShow("Smart Parking", "Se initializeaza");

  FastLED.addLeds<WS2812B, LED_PIN, GRB>(leds, NUM_LEDS).setCorrection(TypicalLEDStrip);
  FastLED.setBrightness(80);
  // Boot state: all spots free → all LEDs green (A1-A5, B1-B5)
  for (int i = 0; i < NUM_LEDS; i++) leds[i] = CRGB::Green;
  FastLED.show();
  Serial.println("FastLED initialised — " + String(NUM_LEDS) + " LEDs (5 coloane × 3 LEDs: A1-A5 + B1-B5)");

  entryServo.attach(SERVO_ENTRY_PIN);
  entryServo.write(SERVO_CLOSED);
  Serial.println("Servo attached — GPIO" + String(SERVO_ENTRY_PIN) + " (used for both entry & exit)");

  // ── Sensors ─────────────────────────────────────────────────────────────────
  dht.begin();
  Serial.println("DHT11 initialised on pin " + String(DHT_PIN));

  // BMP280 mock — senzor absent, valori simulate
  Serial.println("BMP280: mock mode (senzor absent)");

  pinMode(IR_PIN_1,    INPUT);
  pinMode(IR_PIN_2,    INPUT);
  pinMode(MQ4_PIN_1,   INPUT);
  pinMode(MQ4_PIN_2,   INPUT);
  pinMode(FLAME_PIN_1, INPUT_PULLUP);
  pinMode(FLAME_PIN_2, INPUT_PULLUP);
  Serial.println("Sensor pins initialised");

  connectWiFi();
  lcdShow("WiFi conectat", WiFi.localIP().toString().c_str());
  delay(1500);

  mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
  mqttClient.setCallback(onMqttMessage);
  mqttClient.setBufferSize(512);  // Enough for the JSON command payload

  connectMQTT();
  lcdShow("Gata!", "Scanati QR...");
}

// ─── Main loop ────────────────────────────────────────────────────────────────
void loop() {
  // Reconecteaza MQTT doar daca a trecut cel putin 10 s de la ultima incercare
  static unsigned long lastMqttRetry = 0;
  if (!mqttClient.connected()) {
    unsigned long now2 = millis();
    if (now2 - lastMqttRetry >= 10000) {
      lastMqttRetry = now2;
      connectMQTT();
    }
  } else {
    mqttClient.loop();
  }

  checkSpeedTrap();

  unsigned long now = millis();
  if (now - lastEnvPublish >= ENV_PUBLISH_INTERVAL_MS) {
    lastEnvPublish = now;
    publishEnvironment();
  }
  if (now - lastDiagPublish >= DIAG_PUBLISH_INTERVAL_MS) {
    lastDiagPublish = now;
    publishDiagnostics();
  }
}

// ─── Sensor publish helpers ───────────────────────────────────────────────────

/**
 * Speed trap: beam 1 breaks first, then beam 2.
 * Speed = IR_DISTANCE_CM / elapsed_seconds → convert to km/h.
 * Resets after 3 s if only beam 1 ever broke (car stopped / noise).
 */
void checkSpeedTrap() {
  bool b1 = (digitalRead(IR_PIN_1) == LOW);
  bool b2 = (digitalRead(IR_PIN_2) == LOW);
  unsigned long now = millis();

  // Arm on first beam break
  if (b1 && !speedArmed) {
    speedArmed  = true;
    ir1Time     = now;
    Serial.println("[SPEED] Beam 1 broken — armed");
  }

  // Second beam breaks while armed → calculate speed
  if (speedArmed && b2) {
    unsigned long elapsed = now - ir1Time;
    if (elapsed > 0) {
      float distanceM = IR_DISTANCE_CM / 100.0;
      float speedMs   = distanceM / (elapsed / 1000.0);
      float speedKmh  = speedMs * 3.6;

      StaticJsonDocument<128> doc;
      doc["speed_kmh"]    = round(speedKmh * 10) / 10.0;
      doc["elapsed_ms"]   = elapsed;
      char buf[128];
      serializeJson(doc, buf);
      mqttClient.publish(TOPIC_SPEED, buf);
      Serial.printf("[SPEED] %.1f km/h (%lu ms)\n", speedKmh, elapsed);
    }
    speedArmed = false;
  }

  // Timeout — reset if beam 2 never broke within 3 s
  if (speedArmed && (now - ir1Time > 3000)) {
    speedArmed = false;
    Serial.println("[SPEED] Timeout — resetting");
  }
}

/**
 * Reads DHT11, BMP280, MQ-4 gas, and flame sensor then publishes
 * a single JSON payload to parking/environment.
 */
void publishEnvironment() {
  float humidity    = dht.readHumidity();
  float tempDHT     = dht.readTemperature();
  // BMP280 mock — valori simulate realiste
  float tempBMP  = 20.0 + (random(0, 80) / 10.0);   // 20.0–28.0 °C
  float pressure = 1010.0 + (random(0, 150) / 10.0); // 1010–1025 hPa
  int   gas1        = analogRead(MQ4_PIN_1);         // 0–4095
  int   gas2        = analogRead(MQ4_PIN_2);
  bool  flame1      = false; // mock — pinii flotanți produc fals pozitiv
  bool  flame2      = false;

  StaticJsonDocument<256> doc;
  if (!isnan(tempDHT)) doc["temp"]     = round(tempDHT * 10) / 10.0;
  if (!isnan(humidity)) doc["humidity"] = round(humidity * 10) / 10.0;
  if (pressure > 0)     doc["pressure"] = round(pressure * 10) / 10.0;
  if (tempBMP != 0)     doc["bmp_temp"] = round(tempBMP * 10) / 10.0;
  doc["gas1"]   = gas1;
  doc["gas2"]   = gas2;
  doc["flame1"] = flame1;
  doc["flame2"] = flame2;

  char buf[256];
  serializeJson(doc, buf);
  mqttClient.publish(TOPIC_ENV, buf);
  Serial.printf("[ENV] %s\n", buf);
}

/**
 * Publishes raw readings from every sensor pin every 2 s.
 * Used by the dashboard diagnostics panel to verify wiring.
 */
void publishDiagnostics() {
  float humidity = dht.readHumidity();
  float tempDHT  = dht.readTemperature();
  // BMP280 mock — valori simulate realiste
  float tempBMP  = 20.0 + (random(0, 80) / 10.0);
  float pressure = 1010.0 + (random(0, 150) / 10.0);

  StaticJsonDocument<512> doc;

  // DHT11
  doc["dht_temp"]     = isnan(tempDHT) ? -999 : round(tempDHT * 10) / 10.0;
  doc["dht_humidity"] = isnan(humidity) ? -999 : round(humidity * 10) / 10.0;
  doc["dht_ok"]       = !isnan(tempDHT) && !isnan(humidity);

  // BMP280
  doc["bmp_temp"]     = (tempBMP == 0) ? -999 : round(tempBMP * 10) / 10.0;
  doc["bmp_pressure"] = (pressure <= 0) ? -999 : round(pressure * 10) / 10.0;
  doc["bmp_ok"]       = (tempBMP != 0 && pressure > 0);

  // IR speed sensors (raw digital)
  doc["ir1_raw"] = digitalRead(IR_PIN_1);  // 0=beam broken, 1=clear
  doc["ir2_raw"] = digitalRead(IR_PIN_2);
  doc["ir1_ok"]  = true;  // always readable, no failure mode
  doc["ir2_ok"]  = true;

  // MQ-4 gas sensors (raw ADC 0–4095)
  int gas1 = analogRead(MQ4_PIN_1);
  int gas2 = analogRead(MQ4_PIN_2);
  doc["gas1_raw"] = gas1;
  doc["gas2_raw"] = gas2;
  doc["gas1_ok"]  = (gas1 > 0);   // 0 means sensor not connected
  doc["gas2_ok"]  = (gas2 > 0);

  // Flame sensors (raw digital, LOW=flame)
  doc["flame1_raw"]     = 1; // mock HIGH (nicio flacără)
  doc["flame2_raw"]     = 1;
  doc["flame1_detect"]  = false; // mock
  doc["flame2_detect"]  = false;
  doc["flame1_ok"]      = true;
  doc["flame2_ok"]      = true;

  char buf[512];
  serializeJson(doc, buf);
  mqttClient.publish(TOPIC_DIAG, buf);
  Serial.printf("[DIAG] %s\n", buf);
}

// ─── Wi-Fi connection ─────────────────────────────────────────────────────────
void connectWiFi() {
  Serial.printf("Connecting to Wi-Fi: %s", WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.printf("\nWi-Fi connected. IP: %s\n",
                WiFi.localIP().toString().c_str());
}

// ─── MQTT connection (non-blocking, max 3 retries then continue) ─────────────
void connectMQTT() {
  const int MAX_RETRIES = 3;
  int retries = 0;
  while (!mqttClient.connected() && retries < MAX_RETRIES) {
    Serial.printf("Connecting to MQTT broker %s:%d (attempt %d/%d)...",
                  MQTT_BROKER, MQTT_PORT, retries + 1, MAX_RETRIES);
    if (mqttClient.connect(MQTT_CLIENT_ID)) {
      Serial.println(" connected.");
      mqttClient.subscribe(TOPIC_COMMANDS);
      Serial.printf("Subscribed to: %s\n", TOPIC_COMMANDS);
      return;
    } else {
      Serial.printf(" failed (state=%d). Retrying in 3 s...\n",
                    mqttClient.state());
      retries++;
      // Feed watchdog in delay
      for (int i = 0; i < 30; i++) {
        delay(100);
        yield();
      }
    }
  }
  if (!mqttClient.connected()) {
    Serial.println("MQTT: nu s-a putut conecta dupa 3 incercari. Continuam fara MQTT.");
  }
}

// ─── MQTT message handler ─────────────────────────────────────────────────────
void onMqttMessage(char* topic, byte* payload, unsigned int length) {
  // Copy payload and null-terminate so we can treat it as a C-string
  char message[length + 1];
  memcpy(message, payload, length);
  message[length] = '\0';

  Serial.printf("\n[MQTT] Topic  : %s\n", topic);
  Serial.printf("[MQTT] Payload: %s\n", message);

  // ── Parse JSON ──────────────────────────────────────────────────────────────
  StaticJsonDocument<256> doc;
  DeserializationError error = deserializeJson(doc, message);
  if (error) {
    Serial.printf("[MQTT] JSON parse error: %s\n", error.c_str());
    return;
  }

  const char* command = doc["command"];
  const char* spot    = doc["spot"] | "";  // fallback to "" if key is absent

  if (command == nullptr) {
    Serial.println("[MQTT] Missing 'command' field – ignoring message.");
    return;
  }

  Serial.printf("[MQTT] command=%s | spot=%s\n", command, spot);

  // ── Dispatch ────────────────────────────────────────────────────────────────
  if (strcmp(command, "OPEN_ENTRY") == 0) {
    Serial.printf("→ Entry: opening entry barrier for spot %s\n", spot);
    char line2[17];
    snprintf(line2, sizeof(line2), "Mergi la loc: %s", spot);
    lcdShow("Bine ai venit!", line2);
    markSpotOccupied(String(spot));
    openEntryBarrier();
    lcdShow("Gata!", "Scanati QR...");

  } else if (strcmp(command, "OPEN_EXIT") == 0) {
    Serial.println("→ Exit: opening exit barrier.");
    lcdShow("La revedere!", "Drum bun!");
    if (strlen(spot) > 0) {
      markSpotFree(String(spot));
    }
    openExitBarrier();
    delay(1000);
    lcdShow("Gata!", "Scanati QR...");

  } else if (strcmp(command, "RESERVE_SPOT") == 0) {
    // User reserved a spot from app → BLUE
    Serial.printf("→ Rezervare loc %s\n", spot);
    char line2[17];
    snprintf(line2, sizeof(line2), "Rezervat: %s", spot);
    lcdShow("Loc rezervat!", line2);
    markSpotReserved(String(spot));
    delay(1500);
    lcdShow("Gata!", "Scanati QR...");

  } else if (strcmp(command, "CANCEL_RESERVATION") == 0) {
    // Reservation cancelled → back to GREEN
    Serial.printf("→ Anulare rezervare %s\n", spot);
    markSpotUnreserved(String(spot));

  } else {
    Serial.printf("[MQTT] Unknown command '%s' – ignoring.\n", command);
  }
}

// ─── Hardware placeholder functions ──────────────────────────────────────────

/**
 * Opens the entry/exit barrier by rotating a servo motor.
 *
 * TODO – example wiring (servo signal → GPIO 13):
 *   #include <ESP32Servo.h>
 *   Servo barrierServo;
 *   // In setup(): barrierServo.attach(13);
 *
 *   void openEntryBarrier() {
 *     barrierServo.write(90);   // rotate to open position
 *     delay(3000);
 *     barrierServo.write(0);    // rotate back to closed position
 *   }
 */
void openEntryBarrier() {
  Serial.println("[ENTRY] Opening entry barrier...");
  entryServo.write(SERVO_OPEN);
  delay(OPEN_DELAY_MS);
  entryServo.write(SERVO_CLOSED);
  Serial.println("[ENTRY] Entry barrier closed.");
}

void openExitBarrier() {
  Serial.println("[EXIT] Opening exit barrier (same servo as entry)...");
  entryServo.write(SERVO_OPEN);
  delay(OPEN_DELAY_MS);
  entryServo.write(SERVO_CLOSED);
  Serial.println("[EXIT] Exit barrier closed.");
}

// ─── WS2812B LED helpers ──────────────────────────────────────────────────────

/**
 * Returns the column index (0-9) for a spot name, or -1 if invalid.
 * A1/B1 → 0, A2/B2 → 1 … A10/B10 → 9
 */
int spotToColumn(String spot) {
  char zone = spot.charAt(0);
  if ((zone != 'A' && zone != 'B') || spot.length() < 2) return -1;
  int num = spot.substring(1).toInt() - 1;
  if (num < 0 || num >= 5) return -1;  // only A1-A5, B1-B5
  return num;
}

/**
 * Spot colour priority: occupied=RED > reserved=BLUE > free=GREEN
 *
 *   leds[idx+0] = A-row side
 *   leds[idx+1] = middle (reflects worst state of the column)
 *   leds[idx+2] = B-row side
 */
CRGB spotColor(bool occupied, bool reserved) {
  if (occupied) return CRGB::Red;
  if (reserved) return CRGB::Blue;
  return CRGB::Green;
}

void updateColumnLed(int col) {
  int idx = col * LEDS_PER_SPOT;
  leds[idx + 0] = spotColor(occupiedA[col], reservedA[col]);
  leds[idx + 2] = spotColor(occupiedB[col], reservedB[col]);
  // middle LED: worst state of the two spots in the column
  bool midOccupied = occupiedA[col] || occupiedB[col];
  bool midReserved = reservedA[col] || reservedB[col];
  leds[idx + 1] = spotColor(midOccupied, midReserved);
  FastLED.show();
  Serial.printf("[LED] col %d → A:%s mid:%s B:%s\n", col,
    occupiedA[col] ? "RED" : (reservedA[col] ? "BLU" : "GRN"),
    midOccupied    ? "RED" : (midReserved    ? "BLU" : "GRN"),
    occupiedB[col] ? "RED" : (reservedB[col] ? "BLU" : "GRN"));
}

/** Mark a spot as occupied (clears reserved). */
void markSpotOccupied(String spot) {
  int col = spotToColumn(spot);
  if (col < 0) { Serial.printf("[LED] Unknown spot %s\n", spot.c_str()); return; }
  if (spot.charAt(0) == 'A') { occupiedA[col] = true;  reservedA[col] = false; }
  else                        { occupiedB[col] = true;  reservedB[col] = false; }
  updateColumnLed(col);
}

/** Mark a spot as free (clears both occupied and reserved). */
void markSpotFree(String spot) {
  int col = spotToColumn(spot);
  if (col < 0) return;
  if (spot.charAt(0) == 'A') { occupiedA[col] = false; reservedA[col] = false; }
  else                        { occupiedB[col] = false; reservedB[col] = false; }
  updateColumnLed(col);
}

/** Mark a spot as reserved → BLUE. */
void markSpotReserved(String spot) {
  int col = spotToColumn(spot);
  if (col < 0) return;
  if (spot.charAt(0) == 'A') { reservedA[col] = true;  occupiedA[col] = false; }
  else                        { reservedB[col] = true;  occupiedB[col] = false; }
  updateColumnLed(col);
}

/** Cancel reservation → back to GREEN (if not occupied). */
void markSpotUnreserved(String spot) {
  int col = spotToColumn(spot);
  if (col < 0) return;
  if (spot.charAt(0) == 'A') reservedA[col] = false;
  else                        reservedB[col] = false;
  updateColumnLed(col);
}

// ─── LCD helper ───────────────────────────────────────────────────────────────
void lcdShow(const char* line1, const char* line2) {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(line1);
  lcd.setCursor(0, 1);
  lcd.print(line2);
}
