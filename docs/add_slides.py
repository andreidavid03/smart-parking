import copy
from lxml import etree
from pptx import Presentation
from pptx.util import Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
import shutil

BG      = RGBColor(0x0D, 0x1B, 0x2A)
TEAL    = RGBColor(0x00, 0xC4, 0x8C)
BLUE    = RGBColor(0x63, 0x8E, 0xFF)
ORANGE  = RGBColor(0xF5, 0xA6, 0x23)
RED     = RGBColor(0xE5, 0x3E, 0x3E)
CARD_BG = RGBColor(0x1B, 0x2F, 0x45)
TITLE_C = RGBColor(0xE8, 0xED, 0xF2)
MUTED   = RGBColor(0x7A, 0x93, 0xAB)
TOPBAR  = RGBColor(0x00, 0xC4, 0x8C)


def add_rect(slide, l, t, w, h, fill_color):
    shape = slide.shapes.add_shape(1, l, t, w, h)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    shape.line.fill.background()
    return shape


def add_textbox(slide, l, t, w, h, text, bold, size_pt, color, align=PP_ALIGN.LEFT):
    txBox = slide.shapes.add_textbox(l, t, w, h)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.bold = bold
    run.font.size = Pt(size_pt)
    run.font.color.rgb = color
    return txBox


def add_card(slide, l, t, w, h, accent, title, body):
    add_rect(slide, l, t, w, h, CARD_BG)
    add_rect(slide, l, t, Emu(126000), h, accent)
    add_textbox(slide, l + Emu(252000), t + Emu(144000), w - Emu(288000), Emu(396000), title, True, 14, accent)
    add_textbox(slide, l + Emu(252000), t + Emu(612000), w - Emu(288000), Emu(648000), body, False, 13, MUTED)


prs = Presentation('Prezentare_Smart_Parking.pptx')

# ── Slide 11 (index 10): Complete Studiu de piata ───────────────────────────
slide11 = prs.slides[10]

for shape in list(slide11.shapes):
    if shape.name in ('TextBox 34', 'TextBox 37'):
        shape._element.getparent().remove(shape._element)

for shape in slide11.shapes:
    if shape.name == 'TextBox 3' and shape.has_text_frame:
        tf = shape.text_frame
        tf.clear()
        p = tf.paragraphs[0]
        run = p.add_run()
        run.text = 'Studiu de piata & motivatie'
        run.font.bold = True
        run.font.size = Pt(28)
        run.font.color.rgb = TITLE_C

L1, L2 = Emu(288000), Emu(6228000)
W_CARD = Emu(5688000)
H_CARD = Emu(1368000)
R1, R2, R3 = Emu(1368000), Emu(2916000), Emu(4464000)

add_card(slide11, L1, R1, W_CARD, H_CARD, RED,
         '30% din traficul urban',
         'Cauzat de soferi care cauta loc de parcare — studii orase europene')
add_card(slide11, L2, R1, W_CARD, H_CARD, ORANGE,
         'Timp & poluare pierdute',
         'Media: 8 min/sofer pentru gasirea unui loc — emisii CO2 suplimentare evitabile')
add_card(slide11, L1, R2, W_CARD, H_CARD, BLUE,
         'Solutii comerciale — lipsuri',
         'Parkomatic, SmartParking.io: fara GPS integrat, fara QR, fara app mobila completa')
add_card(slide11, L2, R2, W_CARD, H_CARD, TEAL,
         'Noutatea proiectului',
         'Singura solutie open-source cu: senzori IoT + GPS + QR + biometrie + cost automat')
add_card(slide11, L1, R3, W_CARD, H_CARD, ORANGE,
         'Detectie redundanta',
         'Senzori fizici IR + analiza video OpenCV — fallback independent pentru fiabilitate')
add_card(slide11, L2, R3, W_CARD, H_CARD, BLUE,
         'Scalabilitate & cost',
         'Arhitectura modulara NestJS + Docker Compose — extensibil la orice numar de locuri')

print('Slide 11 (Studiu de piata) completed.')

# ── New Bibliografie slide (insert at index 12, before Multumesc) ────────────
layout = prs.slides[11].slide_layout
new_slide = prs.slides.add_slide(layout)

xml_slides = prs.slides._sldIdLst
all_entries = list(xml_slides)
new_entry = all_entries[-1]
xml_slides.remove(new_entry)
target = list(xml_slides)[12]
pos = list(xml_slides).index(target)
xml_slides.insert(pos, new_entry)

bib_slide = prs.slides[12]

for shape in list(bib_slide.shapes):
    shape._element.getparent().remove(shape._element)

add_rect(bib_slide, Emu(0), Emu(0), Emu(12193200), Emu(6858000), BG)
add_rect(bib_slide, Emu(0), Emu(0), Emu(12193200), Emu(108000), TOPBAR)
add_textbox(bib_slide, Emu(540000), Emu(288000), Emu(10440000), Emu(540000),
            'Bibliografie', True, 28, TITLE_C)

refs1 = [
    '[1] Espressif Systems – ESP32 Technical Reference Manual v5.2, 2024\n     https://docs.espressif.com/projects/esp-idf/en/latest/',
    '[2] NestJS – Framework for scalable Node.js apps, 2024\n     https://docs.nestjs.com',
    '[3] Prisma ORM – Next-gen Node.js & TypeScript ORM, 2024\n     https://www.prisma.io/docs',
    '[4] Flutter – Build apps for any screen, Google LLC, 2024\n     https://docs.flutter.dev',
    '[5] Eclipse Mosquitto – Open Source MQTT Broker v2.0\n     https://mosquitto.org/documentation/',
]
refs2 = [
    "[6] Bradski G., Kaehler A. – Learning OpenCV 4\n     O'Reilly Media, 2019",
    '[7] OWASP – Top Ten Security Risks, 2021\n     https://owasp.org/www-project-top-ten/',
    '[8] PostgreSQL Global Dev. Group – PostgreSQL 16 Docs, 2024\n     https://www.postgresql.org/docs/16/',
    '[9] Hunkeler U. et al. – MQTT-S: pub/subscribe for WSN\n     IEEE COMSWARE, 2008',
    '[10] Google LLC – Google Maps Platform Docs, 2024\n      https://developers.google.com/maps',
]

C1, C2 = Emu(288000), Emu(6228000)
CW = Emu(5688000)
ST = Emu(1044000)

for i, ref in enumerate(refs1):
    t = ST + Emu(i * 972000)
    add_rect(bib_slide, C1, t, CW, Emu(900000), CARD_BG)
    add_rect(bib_slide, C1, t, Emu(8000), Emu(900000), TEAL)
    add_textbox(bib_slide, C1 + Emu(72000), t + Emu(72000), CW - Emu(144000), Emu(756000), ref, False, 10.5, MUTED)

for i, ref in enumerate(refs2):
    t = ST + Emu(i * 972000)
    add_rect(bib_slide, C2, t, CW, Emu(900000), CARD_BG)
    add_rect(bib_slide, C2, t, Emu(8000), Emu(900000), BLUE)
    add_textbox(bib_slide, C2 + Emu(72000), t + Emu(72000), CW - Emu(144000), Emu(756000), ref, False, 10.5, MUTED)

print('Bibliografie slide added.')

shutil.copy('Prezentare_Smart_Parking.pptx', 'Prezentare_Smart_Parking.backup.pptx')
prs.save('Prezentare_Smart_Parking.pptx')
print(f'Done. Total slides: {len(prs.slides)}')
