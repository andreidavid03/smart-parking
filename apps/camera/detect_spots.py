#!/usr/bin/env python3
"""
Smart Parking — Camera-based spot occupancy detector
=====================================================
Uses OpenCV background subtraction to decide if each parking spot
is occupied or available, then publishes the result via MQTT to
the topic  parking/sensor/<spot_name>

The NestJS backend subscribes to  parking/sensor/+  and updates
the database — identical to what a physical sensor would do.

Setup
-----
    pip install opencv-python paho-mqtt

Run
---
    python3 detect_spots.py                  # uses config.json
    python3 detect_spots.py --config my.json
    python3 detect_spots.py --show           # open debug window
    python3 detect_spots.py --source 0       # webcam index / RTSP URL

Calibrate ROIs first
--------------------
    python3 calibrate.py   →  prints JSON for config.json spots[]
"""

import cv2
import json
import time
import argparse
import signal
import sys
from collections import deque
from pathlib import Path

try:
    import paho.mqtt.client as mqtt
except ImportError:
    print("ERROR: paho-mqtt not installed.  Run:  pip install paho-mqtt")
    sys.exit(1)


# ── Helpers ───────────────────────────────────────────────────────────────────

def load_config(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


class SpotState:
    """Tracks per-spot debounce state so we don't spam MQTT on every frame."""

    def __init__(self, name: str, debounce: int):
        self.name = name
        self.debounce = debounce
        self._history: deque[bool] = deque(maxlen=debounce)
        self.published: str | None = None   # last published status

    def update(self, occupied: bool) -> str | None:
        """
        Feed a new per-frame observation.
        Returns 'occupied' | 'available' if the stable verdict changed,
        or None if nothing should be published yet.
        """
        self._history.append(occupied)
        if len(self._history) < self.debounce:
            return None   # not enough frames yet

        stable = all(self._history) if occupied else not any(self._history)
        if not stable:
            return None

        verdict = "occupied" if occupied else "available"
        if verdict == self.published:
            return None   # no change

        self.published = verdict
        return verdict


# ── MQTT ──────────────────────────────────────────────────────────────────────

def connect_mqtt(cfg: dict):
    broker = cfg["mqtt"]["broker"]
    port   = cfg["mqtt"]["port"]
    client = mqtt.Client(client_id="camera-detector")

    def on_connect(c, userdata, flags, rc):
        if rc == 0:
            print(f"[MQTT] Connected to {broker}:{port}")
        else:
            print(f"[MQTT] Connection failed rc={rc}")

    client.on_connect = on_connect
    client.connect(broker, port, keepalive=60)
    client.loop_start()
    return client


def publish(client, prefix: str, spot_name: str, status: str):
    topic = f"{prefix}/{spot_name}"
    client.publish(topic, status, qos=1)
    icon = "🔴" if status == "occupied" else "🟢"
    print(f"[MQTT] {icon}  {topic}  →  {status}")


# ── Detection ─────────────────────────────────────────────────────────────────

def roi_occupied(frame_gray, fg_mask, roi, threshold: float, min_area: int) -> bool:
    """
    Returns True if the camera ROI looks occupied.

    Two complementary methods are combined:
    1. Background-subtraction foreground mask — fast, works for newly-parked cars.
    2. Edge density in the grayscale crop — catches cars that were already there
       when the script started (no background model yet for them).
    """
    x, y, w, h = roi

    # --- method 1: foreground mask ---
    roi_fg = fg_mask[y:y+h, x:x+w]
    fg_ratio = cv2.countNonZero(roi_fg) / (w * h)

    # --- method 2: edge density ---
    roi_gray = frame_gray[y:y+h, x:x+w]
    edges = cv2.Canny(roi_gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    large = sum(1 for c in contours if cv2.contourArea(c) >= min_area)

    # Occupied if either method fires
    return fg_ratio > threshold or large >= 1


def draw_debug(frame, spots_cfg, states: list[SpotState]):
    """Overlay coloured ROI rectangles on the debug frame."""
    for spot, state in zip(spots_cfg, states):
        x, y, w, h = spot["roi"]
        occupied = state.published == "occupied"
        color = (0, 0, 220) if occupied else (0, 200, 0)
        label = f"{spot['name']}: {'OCCUPIED' if occupied else 'FREE'}"
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        cv2.putText(frame, label, (x, y - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)
    return frame


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Smart Parking camera detector")
    parser.add_argument("--config", default=str(Path(__file__).parent / "config.json"))
    parser.add_argument("--source", default=None,
                        help="Camera index (0, 1…) or RTSP URL. Overrides config.")
    parser.add_argument("--show", action="store_true",
                        help="Show live debug window with ROI overlays")
    args = parser.parse_args()

    cfg = load_config(args.config)
    cam_cfg  = cfg["camera"]
    det_cfg  = cfg["detection"]
    spots_cfg = cfg["spots"]

    source = int(args.source) if args.source is not None else cam_cfg.get("source", 0)
    if isinstance(source, str) and source.isdigit():
        source = int(source)

    # Open camera
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print(f"ERROR: Cannot open camera source '{source}'")
        sys.exit(1)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  cam_cfg.get("width",  1280))
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_cfg.get("height", 720))

    print(f"[CAM] Opened source {source}  "
          f"{int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}×"
          f"{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")

    # Connect MQTT
    mqtt_client = connect_mqtt(cfg)

    # Background subtractor — learns the empty parking lot
    bg_sub = cv2.createBackgroundSubtractorMOG2(
        history=500, varThreshold=50, detectShadows=True
    )

    # Per-spot state machines
    states = [SpotState(s["name"], det_cfg.get("debounce_frames", 3)) for s in spots_cfg]

    # Graceful shutdown
    running = True
    def _stop(sig, frame):
        nonlocal running
        running = False
    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    fps          = cam_cfg.get("fps", 1)
    warmup       = cam_cfg.get("warmup_frames", 30)
    threshold    = det_cfg.get("occupancy_threshold", 0.15)
    min_area     = det_cfg.get("min_area", 500)
    frame_delay  = max(1, int(1000 / fps))   # ms for cv2.waitKey
    prefix       = cfg["mqtt"]["topic_prefix"]

    frame_idx = 0
    print(f"[CAM] Warming up background model ({warmup} frames)…")

    while running:
        ok, frame = cap.read()
        if not ok:
            print("[CAM] Frame read failed — retrying in 1 s")
            time.sleep(1)
            continue

        gray    = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        fg_mask = bg_sub.apply(frame)

        # Remove shadows (they come back as 127 from MOG2)
        _, fg_mask = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)

        frame_idx += 1
        still_warming = frame_idx <= warmup

        if not still_warming:
            for spot, state in zip(spots_cfg, states):
                occupied = roi_occupied(gray, fg_mask, spot["roi"], threshold, min_area)
                verdict  = state.update(occupied)
                if verdict is not None:
                    publish(mqtt_client, prefix, spot["name"], verdict)

        if args.show:
            debug = draw_debug(frame.copy(), spots_cfg, states)
            if still_warming:
                cv2.putText(debug, f"Warming up… {frame_idx}/{warmup}",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 255), 2)
            cv2.imshow("Smart Parking — Camera Detector", debug)
            key = cv2.waitKey(frame_delay) & 0xFF
            if key == ord("q"):
                break
        else:
            # Headless: respect fps setting
            time.sleep(1.0 / fps)

    cap.release()
    if args.show:
        cv2.destroyAllWindows()
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
    print("[CAM] Stopped.")


if __name__ == "__main__":
    main()
