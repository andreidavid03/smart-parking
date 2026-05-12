#!/usr/bin/env python3
"""
GM65 QR Scanner Bridge (stdin mode)
=====================================
Run this in a VS Code integrated terminal tab.
Before scanning: click once on this terminal so it has focus.
The GM65 types QR code + Enter → this script forwards it to the backend.

Usage:
    /opt/homebrew/bin/python3.13 scanner_bridge.py
"""

import sys
import warnings
warnings.filterwarnings("ignore")
import requests

BACKEND_URL = "http://localhost:3000/parking/hardware-scan"

print("=" * 55)
print("  GM65 QR Scanner Bridge – Smart Parking")
print("=" * 55)
print(f"Backend: {BACKEND_URL}")
print()
print("  ► Click on this terminal, then scan a QR code.")
print("    (No other focus needed — just keep this tab active)")
print()
print("  Press Ctrl+C to quit.")
print()

def send_scan(qr: str):
    print(f"[SCAN] {qr}")
    try:
        r = requests.post(BACKEND_URL, json={"qrCode": qr}, timeout=5)
        data = r.json()
        action = data.get("action", "unknown")
        if action == "entrance":
            spot = data.get("session", {}).get("spot", {}).get("name", "?")
            print(f"[✓]  ENTRY → Spot: {spot}")
        elif action == "exit":
            spot = data.get("session", {}).get("spot", {}).get("name", "?")
            print(f"[✓]  EXIT  → Spot freed: {spot}")
        else:
            print(f"[?]  {data}")
    except requests.exceptions.ConnectionError:
        print("[✗]  Backend unreachable. Is the server running?")
    except Exception as e:
        print(f"[✗]  Error: {e}")
    print()

try:
    for line in sys.stdin:
        qr = line.strip()
        if qr:
            send_scan(qr)
except KeyboardInterrupt:
    print("\nBridge stopped.")



