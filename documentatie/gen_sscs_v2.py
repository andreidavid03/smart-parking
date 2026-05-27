#!/usr/bin/env python3
"""
Generează SSCS_Smart_Parking_Lucrare_v2.docx conform template-ului SSCS-18.
Layout: A4, margini T2.5/B2/L2.5/R2 cm, 2 coloane 7.9cm + 0.7cm + 7.9cm, font Roboto.
"""

from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

FONT = 'Roboto'

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def r(p, text, size=11, bold=False, italic=False):
    """Add a run to paragraph p with Roboto font."""
    run = p.add_run(text)
    run.font.name = FONT
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    return run


def body(doc, text='', size=11, bold=False, italic=False,
         align=WD_ALIGN_PARAGRAPH.JUSTIFY, sb=0, sa=3,
         li=None, ri=None):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_before = Pt(sb)
    p.paragraph_format.space_after = Pt(sa)
    if li is not None:
        p.paragraph_format.left_indent = Cm(li)
    if ri is not None:
        p.paragraph_format.right_indent = Cm(ri)
    if text:
        r(p, text, size=size, bold=bold, italic=italic)
    return p


def h1(doc, text, page_break_before=False):
    """Chapter heading – 11pt, Bold, Justified, UPPERCASE."""
    if page_break_before:
        _page_break(doc)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(3)
    r(p, text.upper(), size=11, bold=True)
    return p


def h2(doc, text):
    """Subchapter heading – 11pt, Bold, Justified."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(0)
    r(p, text, size=11, bold=True)
    return p


def h3(doc, text):
    """Sub-subchapter – 11pt, Italic, Justified."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(0)
    r(p, text, size=11, italic=True)
    return p


def _page_break(doc):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run()
    run.add_break(WD_BREAK.PAGE)
    return p


def fig_caption(doc, num, text):
    """Figure caption – 10pt, Normal, Centered."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(4)
    r(p, f'Fig. {num}. {text}', size=10)
    return p


def fig_placeholder(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(2)
    r(p, f'[ {text} ]', size=10, italic=True)
    return p


def tbl_caption(doc, num, text):
    """Table caption – 10pt, right-aligned, above table."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    r(p, f'Tabelul {num}. {text}', size=10)
    return p


def add_table(doc, headers, rows_data):
    """Add a simple formatted table."""
    num_cols = len(headers)
    tbl = doc.add_table(rows=1 + len(rows_data), cols=num_cols)
    tbl.style = 'Table Grid'
    # Header row
    hdr_cells = tbl.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].text = h
        for run_ in hdr_cells[i].paragraphs[0].runs:
            run_.font.name = FONT
            run_.font.size = Pt(10)
            run_.font.bold = True
    # Data rows
    for ri_, row_data in enumerate(rows_data):
        cells = tbl.rows[ri_ + 1].cells
        for ci, val in enumerate(row_data):
            cells[ci].text = val
            for run_ in cells[ci].paragraphs[0].runs:
                run_.font.name = FONT
                run_.font.size = Pt(10)
    return tbl


def add_hr(doc):
    """Add a paragraph with a bottom border (horizontal rule effect)."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    top = OxmlElement('w:top')
    top.set(qn('w:val'), 'single')
    top.set(qn('w:sz'), '6')
    top.set(qn('w:space'), '1')
    top.set(qn('w:color'), '000000')
    pBdr.append(top)
    pPr.append(pBdr)
    return p


def setup_page(section):
    section.page_height = Cm(29.7)
    section.page_width = Cm(21.0)
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.0)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.0)
    section.header_distance = Cm(1.5)
    section.footer_distance = Cm(1.5)


def setup_header(section):
    hdr = section.header
    hp = hdr.paragraphs[0]
    hp.clear()
    hp.alignment = WD_ALIGN_PARAGRAPH.LEFT
    pPr = hp._p.get_or_add_pPr()
    # Right tab at 16.5cm text width (in twips: ~9355)
    tabs_el = OxmlElement('w:tabs')
    tab_el = OxmlElement('w:tab')
    tab_el.set(qn('w:val'), 'right')
    tab_el.set(qn('w:pos'), '9355')
    tabs_el.append(tab_el)
    pPr.append(tabs_el)
    # Bottom border
    pBdr = OxmlElement('w:pBdr')
    bot = OxmlElement('w:bottom')
    bot.set(qn('w:val'), 'single')
    bot.set(qn('w:sz'), '6')
    bot.set(qn('w:space'), '1')
    bot.set(qn('w:color'), '000000')
    pBdr.append(bot)
    pPr.append(pBdr)
    r1 = hp.add_run('SCIENTIFIC PAPERS')
    r1.font.name = FONT; r1.font.size = Pt(9)
    hp.add_run('\t')
    r2 = hp.add_run('SSCS – 18v')
    r2.font.name = FONT; r2.font.size = Pt(9)


def setup_footer(section):
    ftr = section.footer
    fp = ftr.paragraphs[0]
    fp.clear()
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = fp.add_run('A 18-a Sesiune Studențească de Comunicări Științifice, 22 mai 2026')
    r1.font.name = FONT; r1.font.size = Pt(9)


def set_two_columns(section):
    """Configure section for 2 columns: each 7.9cm, spacing 0.7cm."""
    sectPr = section._sectPr
    for child in sectPr.findall(qn('w:cols')):
        sectPr.remove(child)
    cols = OxmlElement('w:cols')
    cols.set(qn('w:num'), '2')
    cols.set(qn('w:equalWidth'), '0')
    # 7.9cm ≈ 4481 twips; 0.7cm ≈ 397 twips (1cm = 566.929 twips)
    col1 = OxmlElement('w:col')
    col1.set(qn('w:w'), '4481')
    col1.set(qn('w:space'), '397')
    cols.append(col1)
    col2 = OxmlElement('w:col')
    col2.set(qn('w:w'), '4481')
    cols.append(col2)
    sectPr.append(cols)


# ─────────────────────────────────────────────────────────────
# BUILD DOCUMENT
# ─────────────────────────────────────────────────────────────

doc = Document()

# Remove default empty paragraph
for p in doc.paragraphs:
    p._element.getparent().remove(p._element)

# ════════════════════════════════════════════════════════════
# SECTION 1 – Title block (single column, full page width)
# ════════════════════════════════════════════════════════════
sec1 = doc.sections[0]
setup_page(sec1)
setup_header(sec1)
setup_footer(sec1)

# ── TITLU ──────────────────────────────────────────────────
p = body(doc, align=WD_ALIGN_PARAGRAPH.CENTER, sb=6, sa=2)
r(p, 'SISTEM DE PARCARE INTELIGENTĂ – SMART PARKING', size=16, bold=True)

p2 = body(doc, align=WD_ALIGN_PARAGRAPH.CENTER, sb=0, sa=6)
r(p2, 'Automatizarea Fluxului de Acces în Centre Comerciale', size=14, bold=True)

# ── AUTOR ──────────────────────────────────────────────────
pa = body(doc, align=WD_ALIGN_PARAGRAPH.CENTER, sb=0, sa=2)
r(pa, 'DAVID Andrei', size=12, bold=True)
sup = pa.add_run('1')
sup.font.name = FONT; sup.font.size = Pt(8); sup.font.superscript = True

# ── COORDONATOR ────────────────────────────────────────────
pc = body(doc, align=WD_ALIGN_PARAGRAPH.CENTER, sb=0, sa=8)
r(pc, 'Conducător științific: Asist. Univ. Drd. Ing. Silvian-Marian Petrică', size=11, bold=True)

# ── REZUMAT ────────────────────────────────────────────────
pabs = body(doc, align=WD_ALIGN_PARAGRAPH.JUSTIFY, sb=0, sa=4, li=1.0, ri=1.0)
r(pabs, 'REZUMAT: ', size=10, bold=True)
r(pabs,
  ('Lucrarea prezintă un sistem integrat de gestiune a parcărilor bazat pe o arhitectură '
   'distribuită ce combină hardware IoT, procesare video și o aplicație mobilă cross-platform. '
   'Sistemul utilizează microcontrolere ESP32 pentru controlul barierelor de acces, al afișajului '
   'LCD 16×2 și al benzii LED WS2812B, iar OpenCV pentru detectarea locurilor libere. '
   'Un server backend NestJS/PostgreSQL expune API REST protejat JWT, cu comunicare '
   'în timp real prin protocolul MQTT. Accesul este securizat prin coduri QR unice '
   'scanate de cititorul hardware GM65. Aplicația Flutter integrează navigare GPS asistată, '
   'autentificare biometrică și un panou de alerte IoT în timp real (viteză, temperatură, '
   'gaz, flacără). Latența totală de la scanare la deschiderea barierei este de 320 ms, '
   'iar precizia detecției video a atins 97,3%.'),
  size=10)

# ── CUVINTE CHEIE ──────────────────────────────────────────
pkw = body(doc, align=WD_ALIGN_PARAGRAPH.JUSTIFY, sb=0, sa=8, li=1.0, ri=1.0)
r(pkw, 'CUVINTE CHEIE: ', size=10, bold=True)
r(pkw, 'parcare inteligentă, IoT, ESP32, Flutter, MQTT', size=10)

# ── AFILIERE (nota de subsol vizuala) ─────────────────────
add_hr(doc)
paff = body(doc, align=WD_ALIGN_PARAGRAPH.JUSTIFY, sb=0, sa=4)
r(paff, '¹ ', size=9, bold=True)
r(paff,
  'Specializarea Automatică și Informatică Aplicată, Facultatea de Hidrotehnică, '
  'Universitatea Tehnică de Construcții București; '
  'E-mail: david.andrei.st@gmail.com',
  size=9)

# ════════════════════════════════════════════════════════════
# SECTION 2 – Body, 2 columns (continuous section break)
# ════════════════════════════════════════════════════════════
sec2 = doc.add_section(WD_SECTION.CONTINUOUS)
setup_page(sec2)
sec2.header.is_linked_to_previous = True
sec2.footer.is_linked_to_previous = True
set_two_columns(sec2)

# ════════════════════════════════════════════════════════════
# 1. INTRODUCERE
# ════════════════════════════════════════════════════════════
h1(doc, '1. Introducere')

body(doc,
     'Creșterea rapidă a numărului de autovehicule în mediile urbane și în centrele comerciale '
     'a generat o criză acută a spațiilor de parcare. Studiul lui Donald Shoup (UCLA) '
     '„Cruising for Parking" (Shoup, 2007) arată că 30% din traficul urban dens este produs '
     'de vehicule în căutarea unui loc liber, cu o durată medie de 8 minute per eveniment. '
     'Raportul INRIX 2025 estimează că fiecare șofer european pierde echivalentul a 800 EUR/an '
     'exclusiv din cauza congestionării generate de lipsa unui sistem de alocare inteligent. '
     'Emisiile suplimentare de CO₂ datorate acestui fenomen depășesc 730 tone/an '
     'într-un singur district comercial de dimensiuni medii.',
     sb=0, sa=3)

body(doc,
     'Soluțiile clasice – bilete fizice, bariere manuale, afișaje cu contor de locuri – '
     'nu răspund cerințelor actuale de automatizare, trasabilitate și experiență utilizator. '
     'Biletele fizice se pierd, generează cozi la casă și pot fi reutilizate fraudulos. '
     'Personalul la cabinele de control implică costuri operaționale ridicate și disponibilitate '
     'redusă în afara orelor de program. Absența navigării GPS interne obligă șoferul să caute '
     'singur locul alocat, anulând beneficiile oricărui sistem de rezervare automată.',
     sb=0, sa=3)

body(doc,
     'Lucrarea prezintă Smart Parking, un sistem integrat care elimină aceste deficiențe '
     'prin acces QR, monitorizare video în timp real cu OpenCV, navigare GPS asistată, '
     'autentificare biometrică și monitorizare continuă a mediului cu alertare automată. '
     'Sistemul a fost implementat și testat pe un prototip fizic funcțional, '
     'demonstrând aplicabilitate directă în centre comerciale.',
     sb=0, sa=3)

# ════════════════════════════════════════════════════════════
# 2. STADIUL ACTUAL
# ════════════════════════════════════════════════════════════
h1(doc, '2. Stadiul Actual', page_break_before=True)

body(doc,
     'Piața globală a sistemelor de parcare inteligentă a atins 8,5 miliarde USD în 2023 '
     'și este proiectată la 48,3 miliarde USD până în 2033, cu o rată anuală de creștere de 19,3% '
     '(Allied Market Research, 2025). Principalii factori: urbanizarea accelerată, '
     'reglementările de reducere a emisiilor și maturizarea ecosistemului IoT industrial.',
     sb=0, sa=3)

h2(doc, '2.1. Soluții hardware-centricate')
body(doc,
     'Sisteme precum ParkSens și Urbiotica utilizează senzori magnetici sau infraroșu '
     'montați pe fiecare loc pentru a detecta ocuparea și a afișa disponibilitatea pe panouri '
     'exterioare. Aceste soluții nu integrează o componentă mobilă pentru rezervare activă '
     'și nu controlează barierele fizice de acces, limitând semnificativ valoarea adăugată '
     'pentru utilizatorul final și pentru operatorul parcării.',
     sb=0, sa=3)

h2(doc, '2.2. Platforme software de rezervare')
body(doc,
     'Platforme ca Parkopedia și SmartParking.io permit rezervarea prealabilă și plata mobilă, '
     'dar nu integrează controlul fizic al barierelor și nu oferă navigare GPS internă. '
     'Disponibilitatea în timp real depinde de planuri de parcare actualizate manual, '
     'ceea ce introduce latențe și erori în informațiile afișate utilizatorului.',
     sb=0, sa=3)

h2(doc, '2.3. Contribuția propusă')
body(doc,
     'Niciuna dintre soluțiile existente nu acoperă integral lanțul: '
     'hardware IoT + detecție video + control bariere + aplicație mobilă + navigare GPS '
     '+ autentificare securizată + facturare automată + monitorizare mediu cu alerte. '
     'Sistemul propus integrează toate aceste componente folosind exclusiv tehnologii '
     'open-source (ESP32, NestJS, Flutter, PostgreSQL, Mosquitto, OpenCV), '
     'eliminând costurile de licențiere și dependența față de furnizori terți.',
     sb=0, sa=3)

# ════════════════════════════════════════════════════════════
# 3. ARHITECTURA SISTEMULUI
# ════════════════════════════════════════════════════════════
h1(doc, '3. Arhitectura Sistemului', page_break_before=True)

body(doc,
     'Sistemul adoptă o arhitectură pe patru niveluri funcționale (Fig. 1): '
     '(1) nivelul hardware IoT cu module ESP32; '
     '(2) nivelul de procesare video Python/OpenCV; '
     '(3) nivelul backend NestJS/PostgreSQL cu broker MQTT; '
     '(4) nivelul clientului mobil Flutter. '
     'Comunicarea internă ESP32 ↔ backend se realizează prin MQTT (Mosquitto), '
     'iar comunicarea cu aplicația mobilă prin API REST protejat JWT/HTTPS.',
     sb=0, sa=3)

fig_placeholder(doc, 'Figura 1 – Diagrama arhitecturii sistemului Smart Parking')
fig_caption(doc, 1, 'Arhitectura pe 4 niveluri a sistemului Smart Parking.')

h2(doc, '3.1. Hardware IoT – Control și Acces')
body(doc,
     'Subsistemul de control al accesului este construit în jurul unui microcontroler '
     'ESP32 DevKit (Xtensa LX6 dual-core, 240 MHz, Wi-Fi 802.11 b/g/n, 4 MB Flash). '
     'Acesta gestionează: '
     '(a) două servomotoare MG996R pentru barierele de intrare (GPIO18) și ieșire (GPIO19), '
     'setate la 0° (blocat) și 90° (deschis), cu revenire automată după 4 secunde; '
     '(b) un afișaj LCD I2C 16×2 (adresă 0x27, bibliotecă LiquidCrystal_I2C) care afișează '
     'numărul de locuri disponibile și mesaje de status; '
     '(c) o bandă LED WS2812B de 15 LED-uri (GPIO5, rezistor de protecție 330 Ω în serie), '
     'organizată în matrice 5×3 corespunzătoare locurilor A1–A10/B1–B10; '
     'verde = liber (AVAILABLE), albastru = rezervat (RESERVED), roșu = ocupat (OCCUPIED). '
     'Cititorul QR GM65 (interfață USB HID, timp de citire < 100 ms) se conectează '
     'la serverul backend prin scriptul Python scanner_bridge.py. '
     'Un modul ESP32-CAM (AI Thinker, senzor OV2640, 1280×720p) transmite flux MJPEG continuu '
     'procesat de OpenCV pentru detecția locurilor libere.',
     sb=0, sa=3)

h2(doc, '3.2. Hardware IoT – Protecție și Monitorizare')
body(doc,
     'Un set suplimentar de senzori asigură securitatea fizică și monitorizarea mediului. '
     'Doi senzori infraroșu LM393, montați la 10 cm distanță în culoarul de intrare, '
     'formează un speed trap: intervalul de timp dintre cele două întreruperi de fascicol '
     'permite calculul vitezei vehiculului (GPIO34, GPIO35); '
     'o alertă se generează automat dacă viteza depășește pragul configurat (implicit 10 km/h). '
     'Doi senzori MQ-4 (GPIO32, GPIO33) detectează prezența gazului metan/GPL, '
     'iar doi senzori de flacără digitali (GPIO25, GPIO26) asigură detecția incendiului. '
     'Senzorul DHT11 (GPIO4) măsoară temperatura și umiditatea relativă, '
     'iar modulul BMP280 (I2C, adresă 0x76) furnizează presiunea atmosferică. '
     'Toate datele sunt publicate pe topic-ul MQTT parking/diagnostics la fiecare 2 secunde '
     'și pe parking/environment la fiecare 5 secunde.',
     sb=0, sa=3)

h2(doc, '3.3. Componente software – Backend')
body(doc,
     'Backend-ul urmează arhitectura microservicii containerizate prin Docker Compose. '
     'NestJS (TypeScript, Node.js 20) expune API REST pe portul 3000, '
     'organizat în module funcționale: '
     'AuthModule (login, register, JWT RS256, biometrie), '
     'ParkingModule (check-in/out, alocare locuri, gestionare alerte IoT), '
     'SpotsModule (CRUD locuri, coordonate GPS), '
     'MqttModule (comunicare ESP32, procesare evenimente senzori), '
     'EmailModule (verificare cont, resetare parolă prin token hex 32B), '
     'HealthModule (endpoint /health pentru monitoring). '
     'Baza de date PostgreSQL 16 este gestionată prin Prisma ORM cu migrări versionate. '
     'MqttService menține un registru in-memory de alerte (limitat la 200 intrări) '
     'populat automat la detectarea anomaliilor pe parking/diagnostics: '
     'viteză > limita configurată, temperatură > 35°C (avertisment) sau > 40°C (critic), '
     'detecție flacără (critic) sau nivel gaz > 700 (avertisment).',
     sb=0, sa=3)

h2(doc, '3.4. Aplicația mobilă Flutter')
body(doc,
     'Aplicația Flutter (Dart 3, Flutter 3.22) suportă iOS 12+ și Android 8.0+. '
     'Utilizatorul standard dispune de patru file: '
     'cod QR personal, hartă interactivă cu 20 de locuri, '
     'istoric sesiuni cu costul calculat și profil cu preferință loc. '
     'Administratorul dispune de șase file: '
     'Dashboard (statistici timp real – locuri ocupate, rezervate, libere), '
     'Editor (configurare coordonate GPS și tarif orar), '
     'Scanner QR (camera telefonului pentru check-in/out manual), '
     'Camera (flux video live de la ESP32-CAM), '
     'Config (parametri sistem – limită viteză, praguri senzori) '
     'și Alerte (AdminAlertsScreen). '
     'AdminAlertsScreen afișează alertele cu codificare cromatică după severitate '
     '(roșu = critic, portocaliu = avertisment), refresh automat la 5 secunde '
     'și indicator de alerte necitite. '
     'Modul DirectionalNavigationScreen integrează un overlay AnimatedOpacity '
     'care se activează la depășirea limitei de viteză, '
     'afișând valoarea curentă cu indicator vizual și buton de dismiss. '
     'Autentificarea biometrică (Face ID/Touch ID) este gestionată prin '
     'flutter_local_auth, cu stocare securizată prin flutter_secure_storage.',
     sb=0, sa=3)

# ════════════════════════════════════════════════════════════
# 4. IMPLEMENTARE
# ════════════════════════════════════════════════════════════
h1(doc, '4. Implementare', page_break_before=True)

h2(doc, '4.1. Fluxul de acces prin QR și MQTT')
body(doc,
     'Fiecărui utilizator înregistrat i se generează un cod QR hexazecimal unic de 32 de caractere '
     '(128 biți entropie, imposibil de ghicit prin forță brută). '
     'Fluxul complet de intrare se desfășoară în cinci etape: '
     '(1) utilizatorul prezintă telefonul la cititorul GM65; '
     '(2) scriptul scanner_bridge.py publică codul pe topic-ul MQTT parking/entry; '
     '(3) backend-ul identifică utilizatorul, verifică absența unei sesiuni active '
     'și alocă locul optim conform preferinței configurate '
     '(cel mai aproape de intrare, de ieșire, de magazine sau un loc specific); '
     '(4) se publică comanda MQTT {\"command\":\"OPEN_ENTRY\",\"spot\":\"A3\"} – '
     'ESP32-ul deschide bariera, aprinde LED-ul albastru pentru locul rezervat '
     'și actualizează LCD-ul; '
     '(5) sesiunea este înregistrată în PostgreSQL cu timestamp, utilizator și loc alocat. '
     'Întregul ciclu se finalizează în mai puțin de 400 ms. '
     'La ieșire, fluxul simetric cu comanda OPEN_EXIT '
     'finalizează sesiunea, calculează costul (tarif orar × durată în minute / 60) '
     'și îl afișează în istoricul aplicației mobile.',
     sb=0, sa=3)

fig_placeholder(doc, 'Figura 2 – Diagrama secvență flux QR intrare/ieșire')
fig_caption(doc, 2, 'Diagrama secvență – flux complet acces QR prin MQTT.')

h2(doc, '4.2. Detecția video cu OpenCV')
body(doc,
     'Modulul detect_spots.py citește fluxul MJPEG de la ESP32-CAM și aplică '
     'algoritmul BackgroundSubtractorMOG2 (history=500, varThreshold=16) '
     'pe Regiunile de Interes (ROI) definite prin calibrare interactivă (calibrate.py). '
     'Fiecare ROI [x, y, lățime, înălțime] corespunde unui loc de parcare. '
     'Un loc este considerat ocupat dacă fracția de pixeli activi în ROI depășește pragul 0,15. '
     'Un mecanism de debouncing cu fereastră de 3 cadre consecutive '
     'previne tranzițiile false cauzate de umbre, reflexii sau artefacte video temporare. '
     'Starea fiecărui loc este publicată pe MQTT parking/sensor/{spotName} '
     'la fiecare ciclu de 5 secunde, '
     'declanșând actualizarea bazei de date și a benzii LED WS2812B.',
     sb=0, sa=3)

h2(doc, '4.3. Funcționalități mobile cheie')
body(doc,
     'Harta interactivă a parcării afișează în timp real starea celor 20 de locuri '
     '(A1–A10, B1–B10) cu codificare cromatică verde/albastru/roșu, '
     'sincronizată la fiecare 3 secunde cu backend-ul prin polling REST. '
     'La alocarea unui loc, Google Maps SDK lansează navigarea GPS pas cu pas '
     'de la locația curentă a utilizatorului până la coordonatele locului din parcare. '
     'Sesiunea activă afișează un cronometru în timp real și costul estimat calculat local. '
     'Scannerul QR integrat (pachet mobile_scanner) permite administratorului '
     'să proceseze check-in/out manual direct din interfața mobilă, fără hardware fizic. '
     'Funcția de resetare parolă folosește tokenuri expirate la 1 oră, '
     'trimise prin email cu serviciul SMTP configurat (Nodemailer).',
     sb=0, sa=3)

h2(doc, '4.4. Securitate multistrat')
body(doc,
     'Securitatea este implementată pe cinci niveluri complementare: '
     '(1) Stocare parole exclusiv prin bcrypt cu 10 runde de salt (cost factor 2¹⁰); '
     '(2) Autentificare prin token-uri JWT semnate RS256, expirare configurabilă (implicit 24 ore), '
     'verificate la fiecare cerere prin guard-ul AuthGuard; '
     '(3) Verificare obligatorie a adresei de email la înregistrare – '
     'token hex 32B valid 24 ore, trimis prin SMTP și invalitat după utilizare; '
     '(4) Cod QR unic per utilizator cu 128 biți entropie – imposibil de forțat brut; '
     '(5) Comunicare mobilă exclusiv HTTPS; brokerul MQTT izolat în rețeaua Docker privată. '
     'Sistemul respectă principiile OWASP Top 10, '
     'inclusiv validarea strictă a intrărilor prin class-validator și CORS configurat.',
     sb=0, sa=3)

h2(doc, '4.5. Sistem de alerte IoT și monitorizare mediu')
body(doc,
     'MqttService procesează datele primite pe parking/diagnostics și '
     'menține un registru circular in-memory de maxim 200 alerte. '
     'Fiecare alertă stochează: tipul (speed/temperature/flame/gas), '
     'severitatea (warning/critical), valoarea măsurată, descrierea și timestamp-ul ISO 8601. '
     'Pragurile de alertare: viteză > limita din ParkingConfig (implicit 10 km/h), '
     'temperatură > 35°C (avertisment) sau > 40°C (critic), '
     'detecție flacără = critic (prioritate maximă), '
     'nivel gaz > 700 unități analogice = avertisment. '
     'Trei endpoint-uri REST dedicate: '
     'GET /parking/alerts (lista alertelor + câmpul unreadCount), '
     'POST /parking/alerts/read (resetare contor alerte necitite) '
     'și POST /parking/alerts/mock (populare cu 6 alerte de test pentru development). '
     'La primirea oricărei alerte de tip critic, '
     'ESP32-ul primește comanda MQTT de activare a benzii LED WS2812B în modul de urgență '
     '(pulsare roșie la 2 Hz).',
     sb=0, sa=3)

# ════════════════════════════════════════════════════════════
# 5. REZULTATE EXPERIMENTALE
# ════════════════════════════════════════════════════════════
h1(doc, '5. Rezultate Experimentale', page_break_before=True)

body(doc,
     'Sistemul a fost testat pe un prototip fizic funcțional reprezentând o parcare '
     'cu 4 locuri fizice, scalată prin configurație la 20 de locuri logice (A1–A10, B1–B10). '
     'Testele de performanță s-au desfășurat pe o rețea Wi-Fi 2,4 GHz, '
     'pe durata a 72 de ore de funcționare continuă. '
     'Tabelul 1 sintetizează principalii indicatori măsurați.',
     sb=0, sa=3)

tbl_caption(doc, 1, 'Indicatori de performanță măsurați pe prototip.')
add_table(
    doc,
    headers=['Indicator', 'Valoare', 'Referință'],
    rows_data=[
        ('Latență QR → barieră deschisă', '320 ms (medie)', '< 500 ms'),
        ('Precizie detecție video OpenCV', '97,3%', '> 95%'),
        ('Latență actualizare MQTT', '< 1 s', 'Timp real'),
        ('Timp răspuns endpoint REST', '< 80 ms', '< 200 ms'),
        ('Detecție flacără (alerte generate)', '100%', 'Critic'),
        ('Detecție viteză > 10 km/h', '98,5%', 'Avertisment'),
        ('Uptime sistem (72 ore test)', '100%', '> 99,5%'),
    ]
)

body(doc,
     'Latența de 320 ms de la scanare la deschiderea barierei se compune din: '
     'transmisie USB HID cititor → PC (< 50 ms), '
     'procesare cerere REST în backend (~80 ms), '
     'publicare și recepție mesaj MQTT (~60 ms) '
     'și acționare fizică servomotor (~130 ms). '
     'Precizia de 97,3% a detecției OpenCV a fost evaluată pe 300 de capturi '
     'cu ocupare cunoscută, în condiții variate de iluminare. '
     'Principala sursă de eroare (2,7%) a constituit-o reflexia farurilor '
     'vehiculelor pe pardoseala lucioasă în condiții de lumină directă. '
     'Sistemul de alerte IoT a detectat 100% din evenimentele de flacără simulate '
     'și 98,5% din depășirile de viteză înregistrate în sesiunile de test.',
     sb=6, sa=3)

# ════════════════════════════════════════════════════════════
# 6. CONCLUZII
# ════════════════════════════════════════════════════════════
h1(doc, '6. Concluzii', page_break_before=True)

body(doc,
     'Lucrarea prezintă un sistem funcțional și validat de parcare inteligentă '
     'ce integrează hardware IoT, procesare video, comunicare în timp real prin MQTT '
     'și o aplicație mobilă modernă cross-platform. '
     'Arhitectura distribuită, bazată exclusiv pe tehnologii open-source, '
     'asigură scalabilitate orizontală și independență față de furnizori. '
     'Contribuțiile originale ale lucrării includ: '
     '(1) integrarea completă a lanțului hardware–software de la senzor la aplicația mobilă; '
     '(2) subsistemul de alerte IoT cu monitorizare a 6 tipuri de senzori în timp real; '
     '(3) banda LED WS2812B ca interfață vizuală sincronizată cu starea locurilor; '
     '(4) navigarea GPS internă cu overlay de alertă viteză în DirectionalNavigationScreen; '
     '(5) panoul AdminAlertsScreen cu refresh automat și prioritizare cromatică a alertelor.',
     sb=0, sa=3)

body(doc,
     'Rezultatele experimentale confirmă funcționabilitatea sistemului: '
     'latență end-to-end de 320 ms, precizie video de 97,3% și uptime de 100% '
     'pe o perioadă de testare de 72 ore. '
     'Direcțiile viitoare de cercetare includ: '
     '(1) navigare GIS indoor cu integrarea hărții 3D a parcării; '
     '(2) predicția ocupării prin algoritmi de machine learning pe date istorice; '
     '(3) integrarea plății mobile prin NFC sau cod QR dinamic; '
     '(4) extinderea la arhitecturi multi-parcare cu centralizare în cloud.',
     sb=0, sa=3)

# ════════════════════════════════════════════════════════════
# MULȚUMIRI
# ════════════════════════════════════════════════════════════
h1(doc, 'Mulțumiri')

body(doc,
     'Autorul mulțumește conducătorului științific Asist. Univ. Drd. Ing. Silvian-Marian Petrică '
     'pentru îndrumarea continuă pe parcursul elaborării acestei lucrări, '
     'precum și colegilor din Facultatea ETTI – specializarea Automatică și Informatică Aplicată '
     'pentru suportul tehnic acordat în faza de testare a prototipului fizic.',
     sb=0, sa=3)

# ════════════════════════════════════════════════════════════
# BIBLIOGRAFIE
# ════════════════════════════════════════════════════════════
h1(doc, 'Bibliografie')

refs = [
    '[1]. Shoup, D. (2007). Cruising for Parking. Access Magazine, Spring 2007, UC Berkeley.',
    '[2]. INRIX (2025). 2025 Global Traffic Scorecard. Disponibil la: https://inrix.com/scorecard (Accesat: 10.04.2025).',
    '[3]. Allied Market Research (2025). Smart Parking Market Report 2025. https://alliedmarketresearch.com (Accesat: 12.04.2025).',
    '[4]. Espressif Systems (2024). ESP32 Technical Reference Manual v5.2. https://docs.espressif.com.',
    '[5]. NestJS (2024). A progressive Node.js framework for building server-side applications. https://docs.nestjs.com.',
    '[6]. Google LLC (2024). Flutter – Build apps for any screen. https://docs.flutter.dev.',
    '[7]. OpenCV (2024). Open Source Computer Vision Library, versiunea 4.9. https://opencv.org.',
    '[8]. Eclipse Foundation (2024). Eclipse Mosquitto – Open Source MQTT Broker. https://mosquitto.org.',
    '[9]. Prisma (2024). Next-generation ORM for Node.js & TypeScript. https://www.prisma.io/docs.',
    '[10]. UTCB (2026). Regulament sesiune studențească de comunicări științifice AIA – Ediția 18, București.',
]

for ref in refs:
    p = body(doc, ref, size=10, sb=0, sa=2)

# ════════════════════════════════════════════════════════════
# SAVE
# ════════════════════════════════════════════════════════════
out = 'SSCS_Smart_Parking_Lucrare_v2.docx'
doc.save(out)
print(f'Salvat: {out}')
