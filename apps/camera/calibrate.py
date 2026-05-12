#!/usr/bin/env python3
"""
Smart Parking — Interactive ROI Calibration Tool
=================================================
Run this once with your camera connected to draw the bounding boxes
for each parking spot visually. The tool prints a JSON snippet you
can paste directly into config.json → spots[].

Controls (while the window is open)
------------------------------------
  Click + drag   — draw a new ROI box
  SPACE          — confirm current box & advance to next spot
  r              — redo (discard current box and redraw)
  q / ESC        — quit without saving

Usage
-----
    python3 calibrate.py                    # uses config.json for spot names
    python3 calibrate.py --source 1         # use camera index 1
    python3 calibrate.py --spots A1 A2 A3   # override spot names from CLI
"""

import cv2
import json
import argparse
import sys
from pathlib import Path

# ── globals used by the mouse callback ────────────────────────────────────────
_drawing  = False
_start_pt = (0, 0)
_end_pt   = (0, 0)
_confirmed_roi: list[int] | None = None


def _mouse_cb(event, x, y, flags, param):
    global _drawing, _start_pt, _end_pt, _confirmed_roi
    if event == cv2.EVENT_LBUTTONDOWN:
        _drawing = True
        _start_pt = (x, y)
        _end_pt   = (x, y)
        _confirmed_roi = None
    elif event == cv2.EVENT_MOUSEMOVE and _drawing:
        _end_pt = (x, y)
    elif event == cv2.EVENT_LBUTTONUP:
        _drawing = False
        _end_pt = (x, y)


def _roi_from_pts(p1, p2) -> list[int]:
    x = min(p1[0], p2[0])
    y = min(p1[1], p2[1])
    w = abs(p1[0] - p2[0])
    h = abs(p1[1] - p2[1])
    return [x, y, w, h]


def main():
    global _confirmed_roi

    parser = argparse.ArgumentParser(description="ROI calibration tool")
    parser.add_argument("--config", default=str(Path(__file__).parent / "config.json"))
    parser.add_argument("--source", default=None)
    parser.add_argument("--spots", nargs="+", default=None,
                        help="Override spot names, e.g. A1 A2 A3")
    args = parser.parse_args()

    cfg = json.loads(Path(args.config).read_text())
    spot_names = args.spots or [s["name"] for s in cfg["spots"]]

    source = args.source
    if source is None:
        source = cfg["camera"].get("source", 0)
    if isinstance(source, str) and source.isdigit():
        source = int(source)

    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print(f"ERROR: Cannot open camera source '{source}'")
        sys.exit(1)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  cfg["camera"].get("width", 1280))
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cfg["camera"].get("height", 720))

    cv2.namedWindow("Calibrate — Smart Parking", cv2.WINDOW_NORMAL)
    cv2.setMouseCallback("Calibrate — Smart Parking", _mouse_cb)

    results: list[dict] = []
    idx = 0

    print(f"\nCalibrating {len(spot_names)} spots: {spot_names}")
    print("  Click + drag to draw a box, SPACE to confirm, r to redo.\n")

    ok, frame_ref = cap.read()
    if not ok:
        print("ERROR: Could not read first frame")
        sys.exit(1)

    while idx < len(spot_names):
        ok, frame = cap.read()
        if not ok:
            frame = frame_ref.copy()

        display = frame.copy()

        # Draw already-confirmed spots
        for r in results:
            rx, ry, rw, rh = r["roi"]
            cv2.rectangle(display, (rx, ry), (rx+rw, ry+rh), (0, 200, 0), 2)
            cv2.putText(display, r["name"], (rx, ry - 6),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 0), 2)

        # Draw in-progress box
        if _start_pt != _end_pt:
            cv2.rectangle(display, _start_pt, _end_pt, (0, 150, 255), 2)

        name = spot_names[idx]
        cv2.putText(display,
                    f"Draw box for spot: {name}  [{idx+1}/{len(spot_names)}]",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 150, 255), 2)
        cv2.putText(display, "SPACE = confirm   r = redo   q = quit",
                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)

        cv2.imshow("Calibrate — Smart Parking", display)
        key = cv2.waitKey(30) & 0xFF

        if key == ord("q") or key == 27:  # ESC
            print("Calibration aborted.")
            break
        elif key == ord("r"):
            _start_pt = (0, 0); _end_pt = (0, 0)
        elif key == ord(" "):
            if _start_pt != _end_pt:
                roi = _roi_from_pts(_start_pt, _end_pt)
                if roi[2] > 10 and roi[3] > 10:
                    results.append({"name": name, "roi": roi})
                    print(f"  ✓  {name}: {roi}")
                    _start_pt = (0, 0); _end_pt = (0, 0)
                    idx += 1
                else:
                    print("  Box too small, try again.")

    cap.release()
    cv2.destroyAllWindows()

    if results:
        print("\n── Paste this into config.json → \"spots\" ──────────────────")
        print(json.dumps(results, indent=2))
        print("────────────────────────────────────────────────────────────\n")

        # Offer to write back automatically
        try:
            cfg["spots"] = results
            Path(args.config).write_text(json.dumps(cfg, indent=2))
            print(f"✓ config.json updated automatically ({args.config})")
        except Exception as e:
            print(f"Could not auto-save config: {e}")


if __name__ == "__main__":
    main()
