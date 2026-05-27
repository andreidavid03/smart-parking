/*
 * LED TEST — WS2812B pe GPIO5
 * Upload asta pentru a testa strip-ul înainte de a folosi sketch-ul principal.
 *
 * Ce face:
 *  1. Toate LED-urile VERDE  (2 sec) — semnal că totul merge
 *  2. Toate LED-urile ROȘU   (2 sec)
 *  3. Toate LED-urile ALBASTRU (2 sec)
 *  4. Teste individuale — aprinde câte 1 LED pe rând (alb) ca să verifici că
 *     numărul de LED-uri e corect și că nu există LED-uri arse
 *  5. Repeat
 *
 * Conexiune:
 *  ESP32 GPIO5  ──[330Ω]── DIN  (firul de date al strip-ului)
 *  ESP32 GND            ── GND  (firul negru / alb al strip-ului)
 *  5V extern            ── 5V   (firul roșu al strip-ului)
 *  NU alimenta strip-ul direct din 3.3V al ESP32!
 */

#include <FastLED.h>

#define LED_PIN   5
#define NUM_LEDS  15
#define BRIGHTNESS 80

CRGB leds[NUM_LEDS];

void clearAll() {
  fill_solid(leds, NUM_LEDS, CRGB::Black);
  FastLED.show();
}

void allColor(CRGB color, int delayMs) {
  fill_solid(leds, NUM_LEDS, color);
  FastLED.show();
  delay(delayMs);
}

void setup() {
  Serial.begin(115200);
  FastLED.addLeds<WS2812B, LED_PIN, GRB>(leds, NUM_LEDS).setCorrection(TypicalLEDStrip);
  FastLED.setBrightness(BRIGHTNESS);
  clearAll();
  Serial.println("=== LED TEST PORNIT ===");
  Serial.printf("Strip: %d LEDs pe GPIO%d\n", NUM_LEDS, LED_PIN);
}

void loop() {
  // --- Test 1: Verde (locuri libere) ---
  Serial.println("VERDE — toate locurile libere");
  allColor(CRGB::Green, 2000);

  // --- Test 2: Roșu (locuri ocupate) ---
  Serial.println("ROSU — toate locurile ocupate");
  allColor(CRGB::Red, 2000);

  // --- Test 3: Albastru ---
  Serial.println("ALBASTRU");
  allColor(CRGB::Blue, 2000);

  clearAll();
  delay(500);

  // --- Test 4: Individual (verifici că nu e niciun LED ars) ---
  Serial.println("TEST INDIVIDUAL — aprind cate 1 LED...");
  for (int i = 0; i < NUM_LEDS; i++) {
    clearAll();
    leds[i] = CRGB::White;
    FastLED.show();
    Serial.printf("  LED #%d\n", i + 1);
    delay(400);
  }

  clearAll();
  delay(500);

  // --- Test 5: Grup de 3 (simulare loc parcare) ---
  Serial.println("TEST GRUPURI — simulare 5 locuri de parcare (3 LEDs/loc)");
  CRGB spotColors[5] = {CRGB::Green, CRGB::Red, CRGB::Green, CRGB::Red, CRGB::Green};
  for (int spot = 0; spot < 5; spot++) {
    for (int led = 0; led < 3; led++) {
      leds[spot * 3 + led] = spotColors[spot];
    }
  }
  FastLED.show();
  Serial.println("  Verde=liber, Rosu=ocupat");
  delay(3000);

  clearAll();
  delay(1000);
}
