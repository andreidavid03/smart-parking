"""
Generare Fig. 1 – Diagrama arhitecturii sistemului Smart Parking
Output: fig1_architecture.png (1800×900 px, 150 dpi → ~30 × 15 cm la 150 dpi)
"""

from PIL import Image, ImageDraw, ImageFont
import os

OUT = os.path.join(os.path.dirname(__file__), 'fig1_architecture.png')

# ─── Culori SSCS ──────────────────────────────────────────────────────────────
C_DARK   = (0x41, 0x56, 0x6D)   # #41566D albastru-gri
C_GREEN  = (0x84, 0xC4, 0x41)   # #84C441 verde
C_LIGHT  = (0xF3, 0xF2, 0xF4)   # #F3F2F4 gri deschis
C_WHITE  = (0xFF, 0xFF, 0xFF)
C_BLACK  = (0x00, 0x00, 0x00)
C_ARROW  = (0x41, 0x56, 0x6D)

W, H = 1800, 860

img = Image.new('RGB', (W, H), C_WHITE)
draw = ImageDraw.Draw(img)

# ─── Fonturi ──────────────────────────────────────────────────────────────────
def font(size, bold=False):
    """Încearcă să încarce un font system, altfel folosește default."""
    candidates_bold = [
        '/System/Library/Fonts/Supplemental/Arial Bold.ttf',
        '/System/Library/Fonts/Helvetica.ttc',
        '/Library/Fonts/Arial Bold.ttf',
    ]
    candidates_reg = [
        '/System/Library/Fonts/Supplemental/Arial.ttf',
        '/System/Library/Fonts/Helvetica.ttc',
        '/Library/Fonts/Arial.ttf',
    ]
    candidates = candidates_bold if bold else candidates_reg
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()

F_TITLE   = font(28, bold=True)
F_BOX_H   = font(22, bold=True)
F_BOX_S   = font(17)
F_ARROW   = font(15)
F_LAYER   = font(18, bold=True)

# ─── Helpers ──────────────────────────────────────────────────────────────────
def rounded_rect(draw, xy, radius=18, fill=C_LIGHT, outline=C_DARK, width=2):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle([x1, y1, x2, y2], radius=radius,
                           fill=fill, outline=outline, width=width)

def centered_text(draw, xy, text, font, fill=C_DARK):
    x, y = xy
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text((x - tw // 2, y - th // 2), text, font=font, fill=fill)

def multiline_center(draw, cx, top_y, lines, fonts, fills, line_gap=8):
    y = top_y
    for i, (text, fnt, fill) in enumerate(zip(lines, fonts, fills)):
        bbox = draw.textbbox((0, 0), text, font=fnt)
        th = bbox[3] - bbox[1]
        centered_text(draw, (cx, y + th // 2), text, fnt, fill)
        y += th + line_gap
    return y

def arrow_right(draw, x1, y, x2, label='', color=C_ARROW):
    """Săgeată orizontală de la x1 la x2 la înălțimea y."""
    draw.line([(x1, y), (x2, y)], fill=color, width=3)
    # cap săgeată
    draw.polygon([(x2, y), (x2 - 14, y - 7), (x2 - 14, y + 7)], fill=color)
    if label:
        bbox = draw.textbbox((0, 0), label, font=F_ARROW)
        tw = bbox[2] - bbox[0]
        draw.text(((x1 + x2) // 2 - tw // 2, y - 22), label, font=F_ARROW,
                  fill=color)

def arrow_left(draw, x1, y, x2, label='', color=C_ARROW):
    """Săgeată orizontală inversă (de la x1 la x2 < x1)."""
    draw.line([(x1, y), (x2, y)], fill=color, width=3)
    draw.polygon([(x2, y), (x2 + 14, y - 7), (x2 + 14, y + 7)], fill=color)
    if label:
        bbox = draw.textbbox((0, 0), label, font=F_ARROW)
        tw = bbox[2] - bbox[0]
        draw.text(((x1 + x2) // 2 - tw // 2, y + 6), label, font=F_ARROW,
                  fill=color)

def double_arrow(draw, x1, x2, y_up, y_dn, label_up='', label_dn='', color=C_ARROW):
    arrow_right(draw, x1, y_up, x2, label=label_up, color=color)
    arrow_left(draw,  x2, y_dn, x1, label=label_dn, color=color)

# ─── Titlu ────────────────────────────────────────────────────────────────────
centered_text(draw, (W // 2, 38), 'Arhitectura Sistemului Smart Parking',
              F_TITLE, fill=C_DARK)
draw.line([(80, 62), (W - 80, 62)], fill=C_GREEN, width=3)

# ─── Benzi niveluri (fundal colorat) ─────────────────────────────────────────
BAND_Y  = 80
BAND_H  = 740
BAND_W  = 330
GAP     = 60

# 4 coloane: Hardware IoT | Python/OpenCV | Backend | Flutter Mobile
cols_cx = [180, 570, 970, 1370]   # centru X pentru fiecare coloană
col_x1  = [  30, 410, 810, 1210]  # stânga chenar coloană
col_x2  = [ 330, 730, 1130, 1530] # dreapta chenar coloană

layer_colors = [
    (0x41, 0x56, 0x6D, 40),   # gri-albastru transparent
    (0x84, 0xC4, 0x41, 30),
    (0x41, 0x56, 0x6D, 40),
    (0x84, 0xC4, 0x41, 30),
]

layer_titles = [
    'NIVEL 1\nHardware IoT',
    'NIVEL 2\nProcesare Video',
    'NIVEL 3\nBackend',
    'NIVEL 4\nAplicație Mobilă',
]

# Coloane fundal
for i in range(4):
    x1, x2 = col_x1[i], col_x2[i]
    # fundal usor colorat
    bg_color = (C_LIGHT[0], C_LIGHT[1], C_LIGHT[2])
    if i % 2 == 0:
        bg_color = (230, 236, 241)
    else:
        bg_color = (237, 246, 224)
    draw.rectangle([x1, 75, x2, 820], fill=bg_color)
    draw.rectangle([x1, 75, x2, 820], outline=C_DARK, width=1)
    # Titlu nivel
    cx = cols_cx[i]
    lines_t = layer_titles[i].split('\n')
    y_t = 90
    for line in lines_t:
        bbox = draw.textbbox((0,0), line, font=F_LAYER)
        th = bbox[3] - bbox[1]
        centered_text(draw, (cx, y_t + th // 2), line, F_LAYER,
                      fill=C_DARK if i % 2 == 0 else (0x3A, 0x70, 0x1A))
        y_t += th + 4

# ─── Cutii componente ─────────────────────────────────────────────────────────
BOX_W = 260
BOX_H = 70
BOX_H_SMALL = 58

def box(cx, cy, title, subtitle='', color_h=C_DARK, bw=BOX_W, bh=BOX_H):
    x1 = cx - bw // 2
    y1 = cy - bh // 2
    x2 = cx + bw // 2
    y2 = cy + bh // 2
    rounded_rect(draw, [x1, y1, x2, y2], radius=12,
                 fill=C_WHITE, outline=color_h, width=2)
    if subtitle:
        multiline_center(draw, cx, y1 + 10,
                         [title, subtitle],
                         [F_BOX_H, F_BOX_S],
                         [color_h, C_DARK],
                         line_gap=4)
    else:
        centered_text(draw, (cx, cy), title, F_BOX_H, fill=color_h)

# ── Coloana 1: Hardware IoT ──────────────────────────────────────────────────
CX1 = cols_cx[0]
box(CX1, 175, 'ESP32 DevKit',    'Servo + LCD + WS2812B',  C_DARK)
box(CX1, 290, 'ESP32-CAM',       'Stream MJPEG 1280×720',  C_DARK)
box(CX1, 405, 'Scanner GM65',    'USB HID QR < 100 ms',    C_GREEN)
box(CX1, 520, 'Senzori Mediu',   'DHT11, BMP280',           C_DARK, bh=BOX_H_SMALL)
box(CX1, 620, 'Senzori Securit.','MQ-4, Flacără, IR',       C_DARK, bh=BOX_H_SMALL)
box(CX1, 730, 'Servomotoare',    'SG90 GPIO18 / GPIO19',    C_GREEN, bh=BOX_H_SMALL)

# ── Coloana 2: Python/OpenCV ─────────────────────────────────────────────────
CX2 = cols_cx[1]
box(CX2, 195, 'detect_spots.py', 'OpenCV + MOG2 ROI',      C_GREEN)
box(CX2, 320, 'calibrate.py',    'Calibrare interactivă',  C_DARK, bh=BOX_H_SMALL)
box(CX2, 430, 'scanner_bridge.py','QR → MQTT bridge',      C_GREEN)
box(CX2, 545, 'Paho MQTT',       'Publicare parking/sensor',C_DARK, bh=BOX_H_SMALL)

# ── Coloana 3: Backend ────────────────────────────────────────────────────────
CX3 = cols_cx[2]
box(CX3, 175, 'NestJS API',      'REST + JWT (port 3000)',  C_DARK)
box(CX3, 290, 'Mosquitto MQTT',  'Broker port 1883',        C_GREEN)
box(CX3, 405, 'PostgreSQL 16',   'Prisma ORM + migrări',   C_DARK)
box(CX3, 520, 'Docker Compose',  'Containerizare servicii', C_DARK, bh=BOX_H_SMALL)
box(CX3, 620, 'EmailModule',     'Verificare + Reset pwd',  C_DARK, bh=BOX_H_SMALL)

# ── Coloana 4: Mobile ─────────────────────────────────────────────────────────
CX4 = cols_cx[3]
box(CX4, 175, 'Flutter App',     'iOS 12+ / Android 8+',   C_GREEN)
box(CX4, 290, 'Hartă Interactivă','20 locuri live (A1-B10)',C_DARK)
box(CX4, 405, 'Google Maps SDK', 'Navigare GPS pas cu pas', C_GREEN)
box(CX4, 520, 'Biometrie',       'Face ID / Touch ID',      C_DARK, bh=BOX_H_SMALL)
box(CX4, 620, 'flutter_secure\n_storage', 'Keychain / Keystore', C_DARK, bh=BOX_H_SMALL)

# ─── Săgeți între coloane ─────────────────────────────────────────────────────
# Col1 ↔ Col2  (MJPEG stream + MQTT sensor)
AX1R = col_x2[0]
AX2L = col_x1[1]
MID_X12 = (AX1R + AX2L) // 2
arrow_right(draw, AX1R + 2,  250, AX2L - 2,  label='MJPEG stream',   color=C_DARK)
arrow_right(draw, AX1R + 2,  430, AX2L - 2,  label='QR USB HID',    color=C_GREEN)
arrow_left( draw, AX2L - 2,  350, AX1R + 2,  label='MQTT cmds',     color=C_GREEN)

# Col2 ↔ Col3  (MQTT + REST)
AX2R = col_x2[1]
AX3L = col_x1[2]
arrow_right(draw, AX2R + 2,  280, AX3L - 2,  label='MQTT publish',  color=C_GREEN)
arrow_right(draw, AX2R + 2,  440, AX3L - 2,  label='REST /entry',   color=C_DARK)
arrow_left( draw, AX3L - 2,  360, AX2R + 2,  label='MQTT commands', color=C_DARK)

# Col3 ↔ Col4  (REST/HTTPS + JWT)
AX3R = col_x2[2]
AX4L = col_x1[3]
arrow_right(draw, AX3R + 2,  240, AX4L - 2,  label='REST/HTTPS',    color=C_DARK)
arrow_left( draw, AX4L - 2,  320, AX3R + 2,  label='JWT token',     color=C_GREEN)

# ─── Legendă ──────────────────────────────────────────────────────────────────
LEG_Y = 790
draw.line([(80, LEG_Y - 10), (W - 80, LEG_Y - 10)], fill=C_GREEN, width=2)
items = [
    (C_DARK,  '█  Component principal'),
    (C_GREEN, '█  Component IoT / Mobil'),
]
x_leg = 100
for color, text in items:
    bbox = draw.textbbox((0,0), text, font=F_BOX_S)
    draw.text((x_leg, LEG_Y), text, font=F_BOX_S, fill=color)
    x_leg += (bbox[2] - bbox[0]) + 80

centered_text(draw, (W // 2, LEG_Y + 18),
              'Comunicare: MQTT (hardware ↔ backend)  |  REST/HTTPS (mobil ↔ backend)',
              F_ARROW, fill=C_DARK)

# ─── Bordura exterioară ────────────────────────────────────────────────────────
draw.rectangle([5, 5, W - 5, H - 5], outline=C_DARK, width=3)
draw.rectangle([8, 8, W - 8, H - 8], outline=C_GREEN, width=1)

# ─── Salvare ──────────────────────────────────────────────────────────────────
img.save(OUT, 'PNG', dpi=(150, 150))
print(f'✓ Salvat: {OUT}  ({W}×{H} px)')
