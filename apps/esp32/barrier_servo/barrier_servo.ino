/*
 * Smart Parking — Barrier Servo Controller
 * ESP32 + SG90 / MG996R servo
 *
 * Wiring:
 *   Servo signal  → GPIO 18
 *   Servo VCC     → 5V (use external 5V if servo browns out)
 *   Servo GND     → GND (common with ESP32 GND)
 *
 * Libraries needed (Arduino IDE → Library Manager):
 *   - PubSubClient  (Nick O'Leary)
 *   - ESP32Servo    (Kevin Harrington)
 *
 * MQTT topic: parking/commands
 * Expected payloads: {"command":"OPEN_ENTRY"} or {"command":"OPEN_EXIT"}
 * Both open the barrier (same servo), then close after OPEN_DELAY_MS.
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <ESP32Servo.h>

// ─── CONFIG ────────────────────────────────────────────────────────────────
const char* WIFI_SSID     = "YOUR_WIFI_SSID";       // <-- change this
const char* WIFI_PASSWORD  = "YOUR_WIFI_PASSWORD";  // <-- change this
const char* MQTT_BROKER   = "192.168.1.5";           // your Mac's IP (auto-updated by start.py)
const int   MQTT_PORT     = 1883;
const char* MQTT_TOPIC    = "parking/commands";
const char* MQTT_CLIENT_ID = "esp32-barrier";

const int  SERVO_PIN      = 18;
const int  SERVO_OPEN     = 90;   // degrees — barrier arm horizontal (open)
const int  SERVO_CLOSED   = 0;    // degrees — barrier arm vertical (closed)
const int  OPEN_DELAY_MS  = 4000; // how long barrier stays open (ms)
// ────────────────────────────────────────────────────────────────────────────

WiFiClient   wifiClient;
PubSubClient mqtt(wifiClient);
Servo        barrierServo;

bool  isOpen         = false;
long  openedAtMillis = 0;

// ─── WiFi ──────────────────────────────────────────────────────────────────
void connectWiFi() {
  Serial.print("Connecting to WiFi ");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("WiFi connected — IP: ");
  Serial.println(WiFi.localIP());
}

// ─── MQTT callback ─────────────────────────────────────────────────────────
void onMessage(char* topic, byte* payload, unsigned int length) {
  String msg;
  for (unsigned int i = 0; i < length; i++) msg += (char)payload[i];

  Serial.print("MQTT ← ");
  Serial.println(msg);

  if (msg.indexOf("OPEN_ENTRY") >= 0 || msg.indexOf("OPEN_EXIT") >= 0) {
    openBarrier();
  }
}

// ─── MQTT connect/reconnect ────────────────────────────────────────────────
void connectMQTT() {
  while (!mqtt.connected()) {
    Serial.print("Connecting to MQTT broker ");
    Serial.print(MQTT_BROKER);
    Serial.print("...");
    if (mqtt.connect(MQTT_CLIENT_ID)) {
      Serial.println(" connected!");
      mqtt.subscribe(MQTT_TOPIC);
      Serial.print("Subscribed to: ");
      Serial.println(MQTT_TOPIC);
    } else {
      Serial.print(" failed, rc=");
      Serial.print(mqtt.state());
      Serial.println(" — retrying in 3s");
      delay(3000);
    }
  }
}

// ─── Barrier control ───────────────────────────────────────────────────────
void openBarrier() {
  if (isOpen) return; // already open, ignore duplicate command
  Serial.println(">>> Barrier OPEN");
  barrierServo.write(SERVO_OPEN);
  isOpen = true;
  openedAtMillis = millis();
}

void closeBarrier() {
  Serial.println(">>> Barrier CLOSED");
  barrierServo.write(SERVO_CLOSED);
  isOpen = false;
}

// ─── Setup ─────────────────────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  delay(500);

  barrierServo.attach(SERVO_PIN);
  barrierServo.write(SERVO_CLOSED); // start closed
  Serial.println("Servo attached — barrier CLOSED");

  connectWiFi();

  mqtt.setServer(MQTT_BROKER, MQTT_PORT);
  mqtt.setCallback(onMessage);
  connectMQTT();
}

// ─── Loop ──────────────────────────────────────────────────────────────────
void loop() {
  // Reconnect if dropped
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi lost — reconnecting...");
    connectWiFi();
  }
  if (!mqtt.connected()) {
    connectMQTT();
  }
  mqtt.loop();

  // Auto-close after delay
  if (isOpen && (millis() - openedAtMillis >= OPEN_DELAY_MS)) {
    closeBarrier();
  }
}
