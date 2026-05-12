#include <Wire.h>

// GPIO21 = SDA, GPIO22 = SCL (default ESP32)
void setup() {
  Serial.begin(115200);
  delay(1000);
  // Pull-up INAINTE de Wire.begin
  pinMode(21, INPUT_PULLUP);
  pinMode(22, INPUT_PULLUP);
  delay(100);
  Wire.begin(21, 22);
  Wire.setClock(100000); // 100kHz — mai lent, mai stabil
  Serial.println("\n=== I2C Scanner ===");
  Serial.println("SDA=GPIO21, SCL=GPIO22\n");
}

void loop() {
  byte count = 0;
  Serial.println("Scanez bus I2C...");

  for (byte addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    byte err = Wire.endTransmission();
    if (err == 0) {
      Serial.print("  ✓ Dispozitiv gasit la 0x");
      if (addr < 16) Serial.print("0");
      Serial.print(addr, HEX);

      // Identifica dispozitivul
      if (addr == 0x27 || addr == 0x3F) Serial.print("  <- LCD PCF8574");
      if (addr == 0x76)                 Serial.print("  <- BMP280 (SDO=GND)");
      if (addr == 0x77)                 Serial.print("  <- BMP280 (SDO=VCC)");
      if (addr == 0x68 || addr == 0x69) Serial.print("  <- MPU6050");
      Serial.println();
      count++;
    }
  }

  if (count == 0) {
    Serial.println("  ✗ Niciun dispozitiv gasit!");
    Serial.println("    Verifica: fire SDA/SCL, alimentare 3.3V/5V, conexiuni");
  } else {
    Serial.print("  Total: ");
    Serial.print(count);
    Serial.println(" dispozitiv(e) gasit(e)");
  }

  Serial.println();
  delay(3000);
}
