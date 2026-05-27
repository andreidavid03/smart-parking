"""
Generare Fig. 2 – Diagrama secvență flux QR intrare/ieșire cu MQTT
Output: fig2_sequence.png (1600×900 px)
"""

from PIL import Image, ImageDraw, ImageFont
import os

OUT = os.path.join(os.path.dirname(__file__), 'fig2_sequence.png')

C_DARK  = (0x41, 0x56, 0x6D)
C_GREEN = (0x84, 0xC4, 0x41)
C_LIGHT = (0xF3, 0xF2, 0xF4)
C_WHITE = (0xFF, 0xFF, 0xFF)
C_RED   = (0xC0, 0x39, 0x2B)
C_GRAY  = (0xAA, 0xAA, 0xAA)

W, H = 1600, 1280
img = Image.new('RGB', (W, H), C_WHITE)
draw = ImageDraw.Draw(img)

def font(size, bold=False):
    candidates = [
        '/System/Library/Fonts/Supplemental/Arial Bold.ttf' if bold else
        '/System/Library/Fonts/Supplemental/Arial.ttf',
        '/System/Library/Fonts/Helvetica.ttc',
    ]
    for p in candidates:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            pass
    return ImageFont.load_default()

F_TITLE  = font(26, bold=True)
F_ACTOR  = font(18, bold=True)
F_MSG    = font(15)
F_MSG_B  = font(15, bold=True)
F_NOTE   = font(13)
F_LABEL  = font(14, bold=True)

# ─── Titlu ─────────────────────────────────────────────────────────────────
def ctext(draw, cx, cy, text, fnt, fill=C_DARK):
    bb = draw.textbbox((0,0), text, font=fnt)
    tw, th = bb[2]-bb[0], bb[3]-bb[1]
    draw.text((cx - tw//2, cy - th//2), text, font=fnt, fill=fill)

ctext(draw, W//2, 34, 'Diagrama Secvență – Flux Acces QR Intrare / Ieșire cu MQTT',
      F_TITLE, C_DARK)
draw.line([(60, 58), (W-60, 58)], fill=C_GREEN, width=3)

# ─── Actori (coloane) ───────────────────────────────────────────────────────
ACTORS = [
    ('Utilizator\n(Flutter App)', 160),
    ('Scanner\nGM65', 420),
    ('scanner_bridge\n.py', 660),
    ('Backend\n(NestJS)', 900),
    ('Mosquitto\nMQTT', 1110),
    ('ESP32\nDevKit', 1340),
    ('Baza de\nDate', 1540),
]

ACTOR_TOP = 70
ACTOR_BOX_H = 64
LIFELINE_TOP = ACTOR_TOP + ACTOR_BOX_H
LIFELINE_BOT = 1190

# Cutii actori
for name, cx in ACTORS:
    lines = name.split('\n')
    bw = 140
    bh = ACTOR_BOX_H
    x1, y1 = cx - bw//2, ACTOR_TOP
    x2, y2 = cx + bw//2, ACTOR_TOP + bh
    draw.rounded_rectangle([x1, y1, x2, y2], radius=10,
                           fill=C_DARK, outline=C_GREEN, width=2)
    line_h = bh // (len(lines) + 1)
    for i, ln in enumerate(lines):
        ctext(draw, cx, y1 + (i+1)*line_h, ln, F_ACTOR, C_WHITE)
    # Lifeline
    draw.line([(cx, LIFELINE_TOP), (cx, LIFELINE_BOT)],
              fill=C_GRAY, width=1)

# ─── Mesaje ────────────────────────────────────────────────────────────────
MSG_COLOR = C_DARK
RET_COLOR = (0x60, 0x80, 0xA0)

def arrow(x1, x2, y, label, color=MSG_COLOR, ret=False, note=''):
    """Săgeată mesaj orizontală."""
    dash = ret
    if dash:
        # linie întreruptă pentru return
        step = 18
        x = min(x1, x2)
        while x < max(x1, x2) - step:
            draw.line([(x, y), (x+12, y)], fill=color, width=2)
            x += step
        draw.line([(x, y), (max(x1,x2), y)], fill=color, width=2)
    else:
        draw.line([(x1, y), (x2, y)], fill=color, width=2)

    # vârf săgeată
    if x2 > x1:
        draw.polygon([(x2, y), (x2-12, y-6), (x2-12, y+6)], fill=color)
    else:
        draw.polygon([(x2, y), (x2+12, y-6), (x2+12, y+6)], fill=color)

    # label
    mid = (x1 + x2) // 2
    bb = draw.textbbox((0,0), label, font=F_MSG_B if not ret else F_MSG)
    tw = bb[2]-bb[0]
    draw.text((mid - tw//2, y - 20), label, font=F_MSG_B if not ret else F_MSG,
              fill=color)
    if note:
        bb2 = draw.textbbox((0,0), note, font=F_NOTE)
        tw2 = bb2[2]-bb2[0]
        draw.text((mid - tw2//2, y + 5), note, font=F_NOTE, fill=(0x80,0x80,0x80))

def activation(cx, y_start, y_end, color=C_GREEN):
    """Dreptunghi de activare pe lifeline."""
    draw.rectangle([cx-8, y_start, cx+8, y_end], fill=color, outline=C_DARK, width=1)

def divider(y, label):
    """Separator de secțiune cu etichetă."""
    draw.line([(60, y), (W-60, y)], fill=C_LIGHT, width=12)
    draw.line([(60, y), (W-60, y)], fill=C_GREEN, width=2)
    bb = draw.textbbox((0,0), label, font=F_LABEL)
    bw = bb[2]-bb[0]+20
    draw.rectangle([W//2 - bw//2 - 2, y-12, W//2 + bw//2 + 2, y+12],
                   fill=C_GREEN)
    ctext(draw, W//2, y, label, F_LABEL, C_WHITE)

# Helper cx by actor index
cx = [a[1] for a in ACTORS]
U, SC, BR, BE, MQ, ESP, DB = 0,1,2,3,4,5,6

# ══ SECȚIUNEA INTRARE ══════════════════════════════════════════════════════
divider(148, '  INTRARE  ')

Y = 175
activation(cx[U], Y-5, Y+35)
arrow(cx[U], cx[SC], Y, 'Prezintă codul QR', MSG_COLOR)

Y += 55
activation(cx[SC], Y-5, Y+25)
arrow(cx[SC], cx[BR], Y, 'QR string (USB HID)')

Y += 50
activation(cx[BR], Y-5, Y+25)
arrow(cx[BR], cx[BE], Y, 'MQTT: parking/entry', C_GREEN,
      note='  topic: parking/entry  |  payload: { "qr": "a3f9..." }')

Y += 55
activation(cx[BE], Y-5, Y+120)
arrow(cx[BE], cx[DB], Y, 'SELECT user WHERE qr_code = ?')

Y += 45
arrow(cx[DB], cx[BE], Y, 'user = { id, name, preference }', RET_COLOR, ret=True)

Y += 45
arrow(cx[BE], cx[DB], Y, 'INSERT session (user_id, spot, timestamp)')

Y += 45
arrow(cx[DB], cx[BE], Y, 'session_id = 1042', RET_COLOR, ret=True)

Y += 40
arrow(cx[BE], cx[MQ], Y, 'MQTT: parking/commands', C_GREEN,
      note='  { "command": "OPEN_ENTRY", "spot": "A3" }')

Y += 50
activation(cx[MQ], Y-5, Y+25)
arrow(cx[MQ], cx[ESP], Y, 'Forward MQTT command', C_GREEN)

Y += 45
activation(cx[ESP], Y-5, Y+30)
arrow(cx[ESP], cx[U], Y, 'Barieră DESCHISĂ (servo 90°)', RET_COLOR, ret=True)

# ══ SECȚIUNEA IEȘIRE ═══════════════════════════════════════════════════════
divider(Y + 55, '  IEȘIRE  ')
Y += 85

activation(cx[U], Y-5, Y+35)
arrow(cx[U], cx[SC], Y, 'Prezintă codul QR (ieșire)', MSG_COLOR)

Y += 55
activation(cx[SC], Y-5, Y+25)
arrow(cx[SC], cx[BR], Y, 'QR string (USB HID)')

Y += 50
activation(cx[BR], Y-5, Y+25)
arrow(cx[BR], cx[BE], Y, 'MQTT: parking/exit', C_GREEN,
      note='  topic: parking/exit  |  payload: { "qr": "a3f9..." }')

Y += 55
activation(cx[BE], Y-5, Y+80)
arrow(cx[BE], cx[DB], Y, 'UPDATE session SET end_time, cost')

Y += 45
arrow(cx[DB], cx[BE], Y, 'cost = 4.50 RON', RET_COLOR, ret=True)

Y += 45
arrow(cx[BE], cx[MQ], Y, 'MQTT: parking/commands', C_GREEN,
      note='  { "command": "OPEN_EXIT", "spot": "A3" }')

Y += 50
activation(cx[MQ], Y-5, Y+25)
arrow(cx[MQ], cx[ESP], Y, 'Forward MQTT command', C_GREEN)

Y += 45
activation(cx[ESP], Y-5, Y+30)
arrow(cx[ESP], cx[U], Y, 'Barieră DESCHISĂ – sesiune închisă', RET_COLOR, ret=True)

# ─── Latență totală ────────────────────────────────────────────────────────
note_y = LIFELINE_BOT - 100
draw.rounded_rectangle([80, note_y - 18, 520, note_y + 18],
                       radius=8, fill=(0xFF,0xFF,0xE0), outline=C_GREEN, width=2)
ctext(draw, 300, note_y, '⏱  Latență totală intrare: ~ 320 ms  (rețea Wi-Fi 2.4 GHz)',
      F_NOTE, C_DARK)

# ─── Lifeline jos ─────────────────────────────────────────────────────────
for name, acx in ACTORS:
    lines = name.split('\n')
    bw = 140
    bh = ACTOR_BOX_H
    x1, y1 = acx - bw//2, LIFELINE_BOT
    x2, y2 = acx + bw//2, LIFELINE_BOT + bh
    draw.rounded_rectangle([x1, y1, x2, y2], radius=10,
                           fill=C_DARK, outline=C_GREEN, width=2)
    line_h = bh // (len(lines) + 1)
    for i, ln in enumerate(lines):
        ctext(draw, acx, y1 + (i+1)*line_h, ln, F_ACTOR, C_WHITE)

# ─── Bordura ──────────────────────────────────────────────────────────────
draw.rectangle([3, 3, W-3, H-3], outline=C_DARK, width=3)
draw.rectangle([6, 6, W-6, H-6], outline=C_GREEN, width=1)

img.save(OUT, 'PNG', dpi=(150, 150))
print(f'✓ Salvat: {OUT}  ({W}×{H} px)')
