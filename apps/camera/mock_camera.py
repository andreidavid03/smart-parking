#!/usr/bin/env python3
"""
Smart Parking — Mock Camera (fără OpenCV)
==========================================
Simulează detecția vehiculelor pentru demo / prezentare când
camera reală sau OpenCV nu este disponibilă.

Publică aceleași mesaje MQTT ca detect_spots.py:
  parking/sensor/<spot>  →  occupied | available
  (Backend-ul publică automat VEHICLE_DETECTED/VEHICLE_LEFT la ESP32)

Moduri de rulare
----------------
  python3 mock_camera.py                     # keyboard interactiv
  python3 mock_camera.py --auto              # ciclu automat (demo)
  python3 mock_camera.py --auto --interval 6 # ciclu la 6s per pas

Comenzi interactive (keyboard)
-------------------------------
  1-5   Toggle spot A1-A5 (ocupat / liber)
  a     Marchează TOATE ca ocupate
  f     Marchează TOATE ca libere
  q     Ieșire

Config MQTT (același broker ca restul sistemului)
-------------------------------------------------
  --broker  IP broker  (default: localhost)
  --port    Port       (default: 1883)
"""

import json
import time
import argparse
import sys

try:
    import paho.mqtt.client as mqtt
except ImportError:
    print("ERROR: paho-mqtt not installed.  Run:  pip install paho-mqtt")
    sys.exit(1)

SPOTS = ["A1", "A2", "A3", "A4", "A5"]


# ── MQTT client ───────────────────────────────────────────────────────────────

class MockCamera:
    def __init__(self, broker: str, port: int, prefix: str):
        self.prefix = prefix
        self.state = {s: "available" for s in SPOTS}

        self.client = mqtt.Client(client_id="mock-camera")
        self.client.on_connect = self._on_connect
        self.client.connect(broker, port, keepalive=60)
        self.client.loop_start()
        time.sleep(0.6)   # allow connection to settle

    def _on_connect(self, c, userdata, flags, rc):
        status = "connectat" if rc == 0 else f"EROARE rc={rc}"
        print(f"[MQTT] {status}")

    def _publish_spot(self, spot: str, status: str):
        topic = f"{self.prefix}/{spot}"
        self.client.publish(topic, status, qos=1)
        icon = "🔴" if status == "occupied" else "🟢"
        print(f"\n[MOCK] {icon}  {topic}  →  {status}")

    def toggle(self, spot: str):
        new = "occupied" if self.state[spot] == "available" else "available"
        self.state[spot] = new
        self._publish_spot(spot, new)

    def set_spot(self, spot: str, status: str):
        if self.state[spot] != status:
            self.state[spot] = status
            self._publish_spot(spot, status)

    def set_all(self, status: str):
        for s in SPOTS:
            self.set_spot(s, status)

    def print_state(self):
        icons = {"occupied": "🔴", "available": "🟢"}
        row = "  ".join(f"{s}:{icons[self.state[s]]}" for s in SPOTS)
        print(f"[STATE] {row}", flush=True)

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()


# ── Auto-demo mode ────────────────────────────────────────────────────────────

def run_auto(cam: MockCamera, interval: float):
    """
    Scenariu demo:
      1) Umple locurile unul câte unul (A1→A5) — simulate vehicule care parchez
      2) Eliberează locurile unul câte unul — simulate vehicule care pleacă
      3) Ciclul se reia
    """
    print(f"\n[AUTO] Demo ciclu — {interval}s / pas.  Ctrl+C pentru stop.\n")
    step = 0
    n = len(SPOTS)
    try:
        while True:
            phase = step % (n * 2)
            if phase < n:
                cam.set_spot(SPOTS[phase], "occupied")
            else:
                cam.set_spot(SPOTS[phase - n], "available")
            cam.print_state()
            step += 1
            time.sleep(interval)
    except KeyboardInterrupt:
        pass


# ── Interactive mode ──────────────────────────────────────────────────────────

def run_interactive(cam: MockCamera):
    print("\n[INTERACTIV] Comenzi:")
    print("  1-5   Toggle A1-A5 (ocupat/liber)")
    print("  a     Toate OCUPATE")
    print("  f     Toate LIBERE")
    print("  q     Ieșire\n")
    cam.print_state()

    try:
        import tty, termios, select
    except ImportError:
        # Windows fallback — use input()
        _run_interactive_windows(cam)
        return

    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        import tty
        tty.setraw(fd)
        while True:
            rdy = select.select([sys.stdin], [], [], 0.1)[0]
            if not rdy:
                continue
            ch = sys.stdin.read(1)
            if ch == 'q':
                break
            elif ch in '12345':
                cam.toggle(SPOTS[int(ch) - 1])
            elif ch == 'a':
                cam.set_all("occupied")
            elif ch == 'f':
                cam.set_all("available")
            cam.print_state()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
        print()


def _run_interactive_windows(cam: MockCamera):
    """Simple line-based fallback for Windows (no raw tty)."""
    print("(Windows mode — tastează comanda + Enter)")
    while True:
        cmd = input("> ").strip().lower()
        if cmd == 'q':
            break
        elif cmd in '12345':
            cam.toggle(SPOTS[int(cmd) - 1])
        elif cmd == 'a':
            cam.set_all("occupied")
        elif cmd == 'f':
            cam.set_all("available")
        cam.print_state()


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Smart Parking — Mock Camera (fără OpenCV)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--broker",   default="localhost",     help="MQTT broker IP")
    parser.add_argument("--port",     type=int, default=1883,  help="MQTT broker port")
    parser.add_argument("--prefix",   default="parking/sensor", help="MQTT topic prefix")
    parser.add_argument("--auto",     action="store_true",     help="Ciclu automat demo")
    parser.add_argument("--interval", type=float, default=6.0, help="Secunde între pași auto (default: 6)")
    args = parser.parse_args()

    print("🅿️  Smart Parking — Mock Camera")
    print(f"   Broker : {args.broker}:{args.port}")
    print(f"   Mod    : {'AUTO demo' if args.auto else 'interactiv (tastatură)'}")
    if args.auto:
        print(f"   Interval: {args.interval}s / pas")
    print()

    cam = MockCamera(args.broker, args.port, args.prefix)

    try:
        if args.auto:
            run_auto(cam, args.interval)
        else:
            run_interactive(cam)
    except KeyboardInterrupt:
        pass
    finally:
        print("[MOCK] Oprit.")
        cam.stop()


if __name__ == "__main__":
    main()
