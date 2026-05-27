/*
 * Smart Parking — ESP32-CAM MJPEG Stream Server
 * ===============================================
 * Board: AI Thinker ESP32-CAM  (select in Arduino IDE)
 *
 * What it does:
 *   Starts a live MJPEG stream on http://<ESP_IP>/stream
 *   The Python detect_spots.py script reads this URL instead of a USB webcam:
 *     python3 detect_spots.py --source http://<ESP_IP>/stream --show
 *
 * Libraries required:
 *   - ESP32 board package (Espressif Systems) — includes esp_camera, esp_http_server
 *   Install via: Arduino IDE → File → Preferences → add board URL:
 *   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
 *
 * Board settings in Arduino IDE:
 *   Board:            AI Thinker ESP32-CAM
 *   Upload Speed:     115200
 *   Flash Mode:       DIO
 *   Partition Scheme: Huge APP (3MB No OTA/1MB SPIFFS)
 *   Port:             (select your FTDI/USB-TTL adapter port)
 *
 * Wiring (ESP32-CAM has no USB — use FTDI adapter):
 *   ESP32-CAM GND → FTDI GND
 *   ESP32-CAM 5V  → FTDI VCC (5V)
 *   ESP32-CAM U0R → FTDI TX
 *   ESP32-CAM U0T → FTDI RX
 *   GPIO0 → GND during upload, disconnect after upload
 */

#include "esp_camera.h"
#include <WiFi.h>
#include "esp_http_server.h"

// ─── WiFi ─────────────────────────────────────────────────────────────────────
const char* WIFI_SSID     = "campus";       // <-- your WiFi
const char* WIFI_PASSWORD = "barcelona";    // <-- your password

// ─── Camera pin map for AI Thinker ESP32-CAM ──────────────────────────────────
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// ─── MJPEG stream handler ──────────────────────────────────────────────────────
#define PART_BOUNDARY "123456789000000000000987654321"
static const char* STREAM_CONTENT_TYPE =
    "multipart/x-mixed-replace;boundary=" PART_BOUNDARY;
static const char* STREAM_BOUNDARY = "\r\n--" PART_BOUNDARY "\r\n";
static const char* STREAM_PART =
    "Content-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n";

httpd_handle_t stream_httpd = NULL;

static esp_err_t stream_handler(httpd_req_t* req) {
  camera_fb_t* fb       = NULL;
  esp_err_t    res      = ESP_OK;
  size_t       _jpg_buf_len;
  uint8_t*     _jpg_buf;
  char         part_buf[64];

  res = httpd_resp_set_type(req, STREAM_CONTENT_TYPE);
  if (res != ESP_OK) return res;

  while (true) {
    fb = esp_camera_fb_get();
    if (!fb) {
      Serial.println("Camera capture failed");
      res = ESP_FAIL;
      break;
    }

    if (fb->format != PIXFORMAT_JPEG) {
      bool jpeg_converted = frame2jpg(fb, 80, &_jpg_buf, &_jpg_buf_len);
      if (!jpeg_converted) {
        Serial.println("JPEG conversion failed");
        esp_camera_fb_return(fb);
        res = ESP_FAIL;
        break;
      }
    } else {
      _jpg_buf_len = fb->len;
      _jpg_buf     = fb->buf;
    }

    res = httpd_resp_send_chunk(req, STREAM_BOUNDARY, strlen(STREAM_BOUNDARY));
    if (res == ESP_OK) {
      size_t hlen = snprintf(part_buf, sizeof(part_buf), STREAM_PART, _jpg_buf_len);
      res = httpd_resp_send_chunk(req, part_buf, hlen);
    }
    if (res == ESP_OK) {
      res = httpd_resp_send_chunk(req, (const char*)_jpg_buf, _jpg_buf_len);
    }

    if (fb->format != PIXFORMAT_JPEG) free(_jpg_buf);
    esp_camera_fb_return(fb);

    if (res != ESP_OK) break;
  }
  return res;
}

// ─── Single JPEG capture handler (for iOS/Flutter polling) ────────────────────
static esp_err_t capture_handler(httpd_req_t* req) {
  camera_fb_t* fb = esp_camera_fb_get();
  if (!fb) {
    httpd_resp_send_500(req);
    return ESP_FAIL;
  }

  httpd_resp_set_type(req, "image/jpeg");
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  httpd_resp_set_hdr(req, "Cache-Control", "no-cache, no-store");

  esp_err_t res;
  if (fb->format == PIXFORMAT_JPEG) {
    res = httpd_resp_send(req, (const char*)fb->buf, fb->len);
  } else {
    uint8_t* jpg_buf = NULL;
    size_t   jpg_len = 0;
    bool converted = frame2jpg(fb, 80, &jpg_buf, &jpg_len);
    if (converted) {
      res = httpd_resp_send(req, (const char*)jpg_buf, jpg_len);
      free(jpg_buf);
    } else {
      httpd_resp_send_500(req);
      res = ESP_FAIL;
    }
  }
  esp_camera_fb_return(fb);
  return res;
}

// ─── Start HTTP server ─────────────────────────────────────────────────────────
void startStreamServer() {
  httpd_config_t config = HTTPD_DEFAULT_CONFIG();
  config.server_port      = 80;
  config.max_uri_handlers = 4;
  config.max_open_sockets = 5;

  httpd_uri_t stream_uri = {
    .uri       = "/stream",
    .method    = HTTP_GET,
    .handler   = stream_handler,
    .user_ctx  = NULL
  };

  httpd_uri_t capture_uri = {
    .uri       = "/capture",
    .method    = HTTP_GET,
    .handler   = capture_handler,
    .user_ctx  = NULL
  };

  if (httpd_start(&stream_httpd, &config) == ESP_OK) {
    httpd_register_uri_handler(stream_httpd, &stream_uri);
    httpd_register_uri_handler(stream_httpd, &capture_uri);
    Serial.println("Stream server started.");
    Serial.println("  /stream  -> MJPEG continuu");
    Serial.println("  /capture -> JPEG snapshot (pentru iOS/Flutter)");
  }
}

// ─── Setup ────────────────────────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  Serial.println("\n=== Smart Parking ESP32-CAM ===");

  // Camera config
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer   = LEDC_TIMER_0;
  config.pin_d0       = Y2_GPIO_NUM;
  config.pin_d1       = Y3_GPIO_NUM;
  config.pin_d2       = Y4_GPIO_NUM;
  config.pin_d3       = Y5_GPIO_NUM;
  config.pin_d4       = Y6_GPIO_NUM;
  config.pin_d5       = Y7_GPIO_NUM;
  config.pin_d6       = Y8_GPIO_NUM;
  config.pin_d7       = Y9_GPIO_NUM;
  config.pin_xclk     = XCLK_GPIO_NUM;
  config.pin_pclk     = PCLK_GPIO_NUM;
  config.pin_vsync    = VSYNC_GPIO_NUM;
  config.pin_href     = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn     = PWDN_GPIO_NUM;
  config.pin_reset    = RESET_GPIO_NUM;
  config.xclk_freq_hz = 8000000;         // 8MHz — mai compatibil cu module OV2640 ieftine
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size   = FRAMESIZE_QVGA;  // 320x240
  config.jpeg_quality = 12;
  config.fb_count     = 1;

  // ── Fix "I2C bus still busy": elibereaza bus-ul SCCB manual ──────────
  // Daca SDA e tinut LOW de senzor, clock-uim SCL de 9 ori ca sa termine
  // orice tranzactie blocata. Standard I2C bus recovery (SMBUS spec).
  pinMode(SIOC_GPIO_NUM, OUTPUT);
  pinMode(SIOD_GPIO_NUM, INPUT_PULLUP);
  for (int i = 0; i < 9; i++) {
    digitalWrite(SIOC_GPIO_NUM, HIGH);
    delayMicroseconds(10);
    digitalWrite(SIOC_GPIO_NUM, LOW);
    delayMicroseconds(10);
  }
  // STOP condition: SDA LOW→HIGH cu SCL HIGH
  pinMode(SIOD_GPIO_NUM, OUTPUT);
  digitalWrite(SIOC_GPIO_NUM, HIGH);
  delayMicroseconds(10);
  digitalWrite(SIOD_GPIO_NUM, HIGH);
  delayMicroseconds(10);
  // Elibereaza pinii inainte de init (esp_camera ii va reconfigura)
  pinMode(SIOC_GPIO_NUM, INPUT);
  pinMode(SIOD_GPIO_NUM, INPUT);
  delay(50);

  // ── Power-cycle PWDN ──────────────────────────────────────────────────
  if (PWDN_GPIO_NUM != -1) {
    pinMode(PWDN_GPIO_NUM, OUTPUT);
    digitalWrite(PWDN_GPIO_NUM, HIGH); // power down
    delay(300);                        // mai mult timp de discharge
    digitalWrite(PWDN_GPIO_NUM, LOW);  // power up
    delay(300);                        // mai mult timp pentru stabilizare
  }

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed: 0x%x — reincerc...\n", err);
    esp_camera_deinit();
    delay(500);
    if (PWDN_GPIO_NUM != -1) {
      digitalWrite(PWDN_GPIO_NUM, HIGH);
      delay(500);
      digitalWrite(PWDN_GPIO_NUM, LOW);
      delay(200);
    }
    err = esp_camera_init(&config);
    if (err != ESP_OK) {
      Serial.printf("Camera init FAIL definitiv: 0x%x\n", err);
      return;
    }
  }
  Serial.println("Camera ready.");

  // WiFi
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("WiFi connected. Stream URL: http://");
  Serial.print(WiFi.localIP());
  Serial.println("/stream");

  startStreamServer();
}

// ─── Loop ─────────────────────────────────────────────────────────────────────
void loop() {
  delay(10000);
}
