"""
Generator lucrare SSCS v2 – conținut conform SSCS_Smart_Parking_Lucrare_v2.docx
Font: Roboto, A4, margini 2.5 cm, două coloane
Autor: DAVID Andrei
Conducător: Asist. Univ. Drd. Ing. Silvian-Marian Petrică
"""

from docx import Document
from docx.shared import Pt, Cm, RGBColor, Twips
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy, os

FONT = 'Roboto'
OUT  = os.path.join(os.path.dirname(__file__), 'SSCS_Smart_Parking_Lucrare.docx')

# ─── Helpers ─────────────────────────────────────────────────────────────────

def set_font(run, name=FONT, size=None, bold=None, italic=None, color=None):
    run.font.name = name
    rPr = run._r.get_or_add_rPr()
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:ascii'), name)
    rFonts.set(qn('w:hAnsi'), name)
    rFonts.set(qn('w:cs'),    name)
    rPr.insert(0, rFonts)
    if size   is not None: run.font.size   = Pt(size)
    if bold   is not None: run.font.bold   = bold
    if italic is not None: run.font.italic = italic
    if color  is not None: run.font.color.rgb = color


def set_para_fmt(para, align=WD_ALIGN_PARAGRAPH.JUSTIFY,
                 space_before=0, space_after=0,
                 left_indent=None, right_indent=None,
                 line_spacing=WD_LINE_SPACING.SINGLE,
                 sb=None, sa=None):
    if sb is not None: space_before = sb
    if sa is not None: space_after  = sa
    pf = para.paragraph_format
    pf.alignment          = align
    pf.space_before       = Pt(space_before)
    pf.space_after        = Pt(space_after)
    pf.line_spacing_rule  = line_spacing
    if left_indent  is not None: pf.left_indent  = left_indent
    if right_indent is not None: pf.right_indent = right_indent


def add_run(para, text, size=11, bold=False, italic=False, color=None):
    r = para.add_run(text)
    set_font(r, size=size, bold=bold, italic=italic, color=color)
    return r


def para(doc, text='', align=WD_ALIGN_PARAGRAPH.JUSTIFY,
         size=11, bold=False, italic=False, sb=0, sa=0,
         left_indent=None, right_indent=None, color=None):
    p = doc.add_paragraph()
    set_para_fmt(p, align=align, space_before=sb, space_after=sa,
                 left_indent=left_indent, right_indent=right_indent)
    if text:
        add_run(p, text, size=size, bold=bold, italic=italic, color=color)
    return p


def heading(doc, text, size=11, sb=12, sa=3):
    p = doc.add_paragraph()
    set_para_fmt(p, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=sb, space_after=sa)
    add_run(p, text, size=size, bold=True)
    return p


def subheading(doc, text, size=11, sb=6, sa=3):
    p = doc.add_paragraph()
    set_para_fmt(p, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=sb, space_after=sa)
    add_run(p, text, size=size, bold=True, italic=True)
    return p


def body(doc, text, sa=3):
    return para(doc, text, size=11, sa=sa)


def figure_placeholder(doc, fig_num, caption, height_cm=4.5):
    """Chenar placeholder figură + legendă."""
    p_box = doc.add_paragraph()
    set_para_fmt(p_box, align=WD_ALIGN_PARAGRAPH.CENTER, sb=6, sa=0)
    pPr = p_box._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    for side in ('top', 'left', 'bottom', 'right'):
        el = OxmlElement(f'w:{side}')
        el.set(qn('w:val'),   'single')
        el.set(qn('w:sz'),    '12')
        el.set(qn('w:space'), '4')
        el.set(qn('w:color'), '84C441')
        pBdr.append(el)
    pPr.insert(0, pBdr)
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'),   'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'),  'F3F2F4')
    pPr.append(shd)
    r_in = p_box.add_run(f'[ Figura {fig_num} – înlocuiți cu imaginea reală ]')
    set_font(r_in, size=9, italic=True, color=RGBColor(0x84, 0xC4, 0x41))

    lines = max(1, int(height_cm / 0.65))
    for _ in range(lines):
        lp = doc.add_paragraph()
        set_para_fmt(lp, sb=0, sa=0)
        pPr2 = lp._p.get_or_add_pPr()
        pBdr2 = OxmlElement('w:pBdr')
        for side in ('left', 'right'):
            el = OxmlElement(f'w:{side}')
            el.set(qn('w:val'),   'single')
            el.set(qn('w:sz'),    '12')
            el.set(qn('w:space'), '4')
            el.set(qn('w:color'), '84C441')
            pBdr2.append(el)
        pPr2.insert(0, pBdr2)
        shd2 = OxmlElement('w:shd')
        shd2.set(qn('w:val'),   'clear')
        shd2.set(qn('w:color'), 'auto')
        shd2.set(qn('w:fill'),  'F3F2F4')
        pPr2.append(shd2)

    p_bot = doc.add_paragraph()
    set_para_fmt(p_bot, align=WD_ALIGN_PARAGRAPH.CENTER, sb=0, sa=0)
    pPr3 = p_bot._p.get_or_add_pPr()
    pBdr3 = OxmlElement('w:pBdr')
    for side in ('left', 'right', 'bottom'):
        el = OxmlElement(f'w:{side}')
        el.set(qn('w:val'),   'single')
        el.set(qn('w:sz'),    '12')
        el.set(qn('w:space'), '4')
        el.set(qn('w:color'), '84C441')
        pBdr3.append(el)
    pPr3.insert(0, pBdr3)
    shd3 = OxmlElement('w:shd')
    shd3.set(qn('w:val'),   'clear')
    shd3.set(qn('w:color'), 'auto')
    shd3.set(qn('w:fill'),  'F3F2F4')
    pPr3.append(shd3)

    p_cap = doc.add_paragraph()
    set_para_fmt(p_cap, align=WD_ALIGN_PARAGRAPH.CENTER, sb=3, sa=8)
    r_cap = p_cap.add_run(f'Fig. {fig_num}. {caption}')
    set_font(r_cap, size=9, italic=True)
    return p_cap


def add_results_table(doc):
    rows = [
        ('Indicator',                             'Valoare',           'Referință'),
        ('Latență QR → barieră deschisă',         '320 ms (medie)',    '< 500 ms'),
        ('Precizie detecție video OpenCV',         '97,3%',             '> 95%'),
        ('Latență actualizare MQTT',               '< 1 s',             'Timp real'),
        ('Timp răspuns endpoint REST',             '< 80 ms',           '< 200 ms'),
        ('Detecție flacără (alerte generate)',     '100%',              'Critic'),
        ('Detecție viteză > 10 km/h',              '98,5%',             'Avertisment'),
        ('Uptime sistem (72 ore test)',             '100%',              '> 99,5%'),
    ]
    tbl = doc.add_table(rows=len(rows), cols=3)
    tbl.style = 'Table Grid'
    for r_idx, row_data in enumerate(rows):
        row = tbl.rows[r_idx]
        for c_idx, cell_text in enumerate(row_data):
            cell = row.cells[c_idx]
            cell.paragraphs[0].clear()
            p = cell.paragraphs[0]
            set_para_fmt(p, align=WD_ALIGN_PARAGRAPH.CENTER, sb=2, sa=2)
            r = p.add_run(cell_text)
            set_font(r, size=9, bold=(r_idx == 0))
    widths = [Cm(3.5), Cm(2.0), Cm(2.4)]
    for row in tbl.rows:
        for c_idx, cell in enumerate(row.cells):
            tc = cell._tc
            tcPr = tc.get_or_add_tcPr()
            tcW = OxmlElement('w:tcW')
            tcW.set(qn('w:w'),    str(int(widths[c_idx].pt * 20)))
            tcW.set(qn('w:type'), 'dxa')
            tcPr.append(tcW)
    return tbl


def switch_to_two_columns(doc):
    p = doc.add_paragraph()
    pPr = p._p.get_or_add_pPr()
    sectPr = OxmlElement('w:sectPr')
    src_sectPr = doc.sections[0]._sectPr
    for child_tag in (qn('w:pgSz'), qn('w:pgMar')):
        child = src_sectPr.find(child_tag)
        if child is not None:
            sectPr.append(copy.deepcopy(child))
    cols = OxmlElement('w:cols')
    cols.set(qn('w:num'),        '2')
    cols.set(qn('w:space'),      '397')
    cols.set(qn('w:equalWidth'), '1')
    sectPr.append(cols)
    type_elem = OxmlElement('w:type')
    type_elem.set(qn('w:val'), 'continuous')
    sectPr.append(type_elem)
    pPr.append(sectPr)
    set_para_fmt(p, space_before=0, space_after=0)


# ─── Document setup ──────────────────────────────────────────────────────────

doc = Document()
sec = doc.sections[0]
sec.page_width    = Cm(21.0)
sec.page_height   = Cm(29.7)
sec.left_margin   = Cm(2.5)
sec.right_margin  = Cm(2.5)
sec.top_margin    = Cm(2.5)
sec.bottom_margin = Cm(2.5)
sec.header_distance = Cm(1.5)
sec.footer_distance = Cm(1.5)

sn = doc.styles['Normal']
sn.font.name = FONT
sn.font.size = Pt(11)
sn.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
sn.paragraph_format.space_after  = Pt(3)
sn.paragraph_format.space_before = Pt(0)

# ─── HEADER ──────────────────────────────────────────────────────────────────
header = sec.header
hp = header.paragraphs[0]
hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = hp.add_run('A 18-A Sesiune Studențească de Comunicări Științifice – SSCS 2026')
set_font(r, size=9, italic=True)
pPr = hp._p.get_or_add_pPr()
pBdr = OxmlElement('w:pBdr')
btm = OxmlElement('w:bottom')
btm.set(qn('w:val'), 'single'); btm.set(qn('w:sz'), '6')
btm.set(qn('w:space'), '1');    btm.set(qn('w:color'), '000000')
pBdr.append(btm); pPr.append(pBdr)

# ─── FOOTER ──────────────────────────────────────────────────────────────────
footer = sec.footer
fp = footer.paragraphs[0]
fp.clear()
fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
fp.paragraph_format.space_before = Pt(4)
fp.paragraph_format.space_after  = Pt(0)
r0 = fp.add_run('– ')
set_font(r0, size=10)
fld = OxmlElement('w:fldChar'); fld.set(qn('w:fldCharType'), 'begin')
r1e = OxmlElement('w:r'); r1e.append(fld); fp._p.append(r1e)
instr = OxmlElement('w:instrText'); instr.text = ' PAGE '
r2e = OxmlElement('w:r'); r2e.append(instr); fp._p.append(r2e)
fld2 = OxmlElement('w:fldChar'); fld2.set(qn('w:fldCharType'), 'end')
r3e = OxmlElement('w:r'); r3e.append(fld2); fp._p.append(r3e)
r4 = fp.add_run(' –')
set_font(r4, size=10)

# ═══════════════════════════════════════════════════════════════════════════
# TITLU (single column)
# ═══════════════════════════════════════════════════════════════════════════

para(doc,
    'Aplicație mobilă cu integrare hardware pentru optimizarea procesului de parcare '
    'în centre comerciale',
    align=WD_ALIGN_PARAGRAPH.CENTER, size=14, bold=True, sb=0, sa=3)

para(doc, 'DAVID Andrei',
    align=WD_ALIGN_PARAGRAPH.CENTER, size=12, bold=True, sb=4, sa=2)

para(doc,
    'Conducător științific: Asist. Univ. Drd. Ing. Silvian-Marian Petrică',
    align=WD_ALIGN_PARAGRAPH.CENTER, size=11, bold=True, sb=2, sa=6)

# Rezumat
p_rez = doc.add_paragraph()
set_para_fmt(p_rez, align=WD_ALIGN_PARAGRAPH.JUSTIFY, sb=4, sa=4,
             left_indent=Cm(1.0), right_indent=Cm(1.0))
r_lbl = p_rez.add_run('REZUMAT: ')
set_font(r_lbl, size=10, bold=True)
r_txt = p_rez.add_run(
    'Lucrarea prezintă un sistem integrat de gestiune a parcărilor bazat pe o arhitectură '
    'distribuită ce combină hardware IoT, procesare video și o aplicație mobilă cross-platform. '
    'Sistemul utilizează microcontrolere ESP32 pentru controlul barierelor de acces, al '
    'afișajului LCD 16×2 și al benzii LED WS2812B, iar OpenCV pentru detectarea locurilor '
    'libere. Un server backend NestJS/PostgreSQL expune API REST protejat JWT, cu comunicare '
    'în timp real prin protocolul MQTT. Accesul este securizat prin coduri QR unice scanate de '
    'cititorul hardware GM65. Aplicația Flutter integrează navigare GPS asistată, autentificare '
    'biometrică și un panou de alerte IoT în timp real (viteză, temperatură, gaz, flacără). '
    'Latența totală de la scanare la deschiderea barierei este de 320 ms, iar precizia '
    'detecției video a atins 97,3%.')
set_font(r_txt, size=10)

# Cuvinte cheie
p_kw = doc.add_paragraph()
set_para_fmt(p_kw, align=WD_ALIGN_PARAGRAPH.JUSTIFY, sb=4, sa=6,
             left_indent=Cm(1.0), right_indent=Cm(1.0))
r_kw_lbl = p_kw.add_run('CUVINTE CHEIE: ')
set_font(r_kw_lbl, size=10, bold=True)
r_kw = p_kw.add_run('parcare inteligentă, IoT, ESP32, Flutter, MQTT')
set_font(r_kw, size=10)

# Afiliere footnote
p_aff = doc.add_paragraph()
set_para_fmt(p_aff, align=WD_ALIGN_PARAGRAPH.JUSTIFY, sb=4, sa=8,
             left_indent=Cm(0.5), right_indent=Cm(0.5))
r_aff = p_aff.add_run(
    '¹ Specializarea Automatică și Informatică Aplicată, Facultatea de Hidrotehnică, '
    'Universitatea Tehnică de Construcții București; E-mail: andreid094@gmail.com')
set_font(r_aff, size=9, italic=True)

# ═══════════════════════════════════════════════════════════════════════════
# CORP – două coloane
# ═══════════════════════════════════════════════════════════════════════════
switch_to_two_columns(doc)

# ══════════════════════════════════════════════════════════════════════════
# 1. INTRODUCERE
# ══════════════════════════════════════════════════════════════════════════
heading(doc, '1. INTRODUCERE')
body(doc,
    'Creșterea rapidă a numărului de autovehicule în mediile urbane și în centrele '
    'comerciale a generat o criză acută a spațiilor de parcare. Studiul lui Donald Shoup '
    '(UCLA) „Cruising for Parking" (Shoup, 2007) arată că 30% din traficul urban dens este '
    'produs de vehicule în căutarea unui loc liber, cu o durată medie de 8 minute per '
    'eveniment. Raportul INRIX 2025 estimează că fiecare șofer european pierde echivalentul '
    'a 800 EUR/an exclusiv din cauza congestionării generate de lipsa unui sistem de alocare '
    'inteligent. Emisiile suplimentare de CO₂ datorate acestui fenomen depășesc 730 tone/an '
    'într-un singur district comercial de dimensiuni medii.')
body(doc,
    'Soluțiile clasice – bilete fizice, bariere manuale, afișaje cu contor de locuri – nu '
    'răspund cerințelor actuale de automatizare, trasabilitate și experiență utilizator. '
    'Biletele fizice se pierd, generează cozi la casă și pot fi reutilizate fraudulos. '
    'Personalul la cabinele de control implică costuri operaționale ridicate și disponibilitate '
    'redusă în afara orelor de program. Absența navigării GPS interne obligă șoferul să caute '
    'singur locul alocat, anulând beneficiile oricărui sistem de rezervare automată.')
body(doc,
    'Lucrarea prezintă Smart Parking, un sistem integrat care elimină aceste deficiențe prin '
    'acces QR, monitorizare video în timp real cu OpenCV, navigare GPS asistată, autentificare '
    'biometrică și monitorizare continuă a mediului cu alertare automată. Sistemul a fost '
    'implementat și testat pe un prototip fizic funcțional, demonstrând aplicabilitate directă '
    'în centre comerciale.')

# ══════════════════════════════════════════════════════════════════════════
# 2. STADIUL ACTUAL
# ══════════════════════════════════════════════════════════════════════════
heading(doc, '2. STADIUL ACTUAL', sb=10)
body(doc,
    'Piața globală a sistemelor de parcare inteligentă a atins 8,5 miliarde USD în 2023 și '
    'este proiectată la 48,3 miliarde USD până în 2033, cu o rată anuală de creștere de 19,3% '
    '(Allied Market Research, 2025). Principalii factori: urbanizarea accelerată, '
    'reglementările de reducere a emisiilor și maturizarea ecosistemului IoT industrial.')

subheading(doc, '2.1. Soluții hardware-centricate')
body(doc,
    'Sisteme precum ParkSens și Urbiotica utilizează senzori magnetici sau infraroșu montați '
    'pe fiecare loc pentru a detecta ocuparea și a afișa disponibilitatea pe panouri exterioare. '
    'Aceste soluții nu integrează o componentă mobilă pentru rezervare activă și nu controlează '
    'barierele fizice de acces, limitând semnificativ valoarea adăugată pentru utilizatorul '
    'final și pentru operatorul parcării.')

subheading(doc, '2.2. Platforme software de rezervare')
body(doc,
    'Platforme ca Parkopedia și SmartParking.io permit rezervarea prealabilă și plata mobilă, '
    'dar nu integrează controlul fizic al barierelor și nu oferă navigare GPS internă. '
    'Disponibilitatea în timp real depinde de planuri de parcare actualizate manual, ceea ce '
    'introduce latențe și erori în informațiile afișate utilizatorului.')

subheading(doc, '2.3. Contribuția propusă')
body(doc,
    'Niciuna dintre soluțiile existente nu acoperă integral lanțul: hardware IoT + detecție '
    'video + control bariere + aplicație mobilă + navigare GPS + autentificare securizată + '
    'facturare automată + monitorizare mediu cu alerte. Sistemul propus integrează toate '
    'aceste componente folosind exclusiv tehnologii open-source (ESP32, NestJS, Flutter, '
    'PostgreSQL, Mosquitto, OpenCV), eliminând costurile de licențiere și dependența față '
    'de furnizori terți.')

# ══════════════════════════════════════════════════════════════════════════
# 3. ARHITECTURA SISTEMULUI
# ══════════════════════════════════════════════════════════════════════════
heading(doc, '3. ARHITECTURA SISTEMULUI', sb=10)
body(doc,
    'Sistemul adoptă o arhitectură pe patru niveluri funcționale (Fig. 1): (1) nivelul '
    'hardware IoT cu module ESP32; (2) nivelul de procesare video Python/OpenCV; (3) nivelul '
    'backend NestJS/PostgreSQL cu broker MQTT; (4) nivelul clientului mobil Flutter. '
    'Comunicarea internă ESP32 ↔ backend se realizează prin MQTT (Mosquitto), iar '
    'comunicarea cu aplicația mobilă prin API REST protejat JWT/HTTPS.')

figure_placeholder(doc, 1,
    'Arhitectura pe 4 niveluri a sistemului Smart Parking.',
    height_cm=5.0)

subheading(doc, '3.1. Hardware IoT – Control și Acces')
body(doc,
    'Subsistemul de control al accesului este construit în jurul unui microcontroler '
    'ESP32 DevKit (Xtensa LX6 dual-core, 240 MHz, Wi-Fi 802.11 b/g/n, 4 MB Flash). '
    'Acesta gestionează: (a) două servomotoare MG996R pentru barierele de intrare (GPIO18) '
    'și ieșire (GPIO19), setate la 0° (blocat) și 90° (deschis), cu revenire automată după '
    '4 secunde; (b) un afișaj LCD I2C 16×2 (adresă 0x27, bibliotecă LiquidCrystal_I2C) '
    'care afișează numărul de locuri disponibile și mesaje de status; (c) o bandă LED '
    'WS2812B de 15 LED-uri (GPIO5, rezistor de protecție 330 Ω în serie), organizată în '
    'matrice 5×3 corespunzătoare locurilor A1–A10/B1–B10; verde = liber (AVAILABLE), '
    'albastru = rezervat (RESERVED), roșu = ocupat (OCCUPIED). Cititorul QR GM65 '
    '(interfață USB HID, timp de citire < 100 ms) se conectează la serverul backend prin '
    'scriptul Python scanner_bridge.py. Un modul ESP32-CAM (AI Thinker, senzor OV2640, '
    '1280×720p) transmite flux MJPEG continuu procesat de OpenCV pentru detecția '
    'locurilor libere.')

subheading(doc, '3.2. Hardware IoT – Protecție și Monitorizare')
body(doc,
    'Un set suplimentar de senzori asigură securitatea fizică și monitorizarea mediului. '
    'Doi senzori infraroșu LM393, montați la 10 cm distanță în culoarul de intrare, '
    'formează un speed trap: intervalul de timp dintre cele două întreruperi de fascicol '
    'permite calculul vitezei vehiculului (GPIO34, GPIO35); o alertă se generează automat '
    'dacă viteza depășește pragul configurat (implicit 10 km/h). Doi senzori MQ-4 '
    '(GPIO32, GPIO33) detectează prezența gazului metan/GPL, iar doi senzori de flacără '
    'digitali (GPIO25, GPIO26) asigură detecția incendiului. Senzorul DHT11 (GPIO4) '
    'măsoară temperatura și umiditatea relativă, iar modulul BMP280 (I2C, adresă 0x76) '
    'furnizează presiunea atmosferică. Toate datele sunt publicate pe topic-ul MQTT '
    'parking/diagnostics la fiecare 2 secunde și pe parking/environment la fiecare 5 secunde.')

subheading(doc, '3.3. Componente software – Backend')
body(doc,
    'Backend-ul urmează arhitectura microservicii containerizate prin Docker Compose. '
    'NestJS (TypeScript, Node.js 20) expune API REST pe portul 3000, organizat în module '
    'funcționale: AuthModule (login, register, JWT RS256, biometrie), ParkingModule '
    '(check-in/out, alocare locuri, gestionare alerte IoT), SpotsModule (CRUD locuri, '
    'coordonate GPS), MqttModule (comunicare ESP32, procesare evenimente senzori), '
    'EmailModule (verificare cont, resetare parolă prin token hex 32B), HealthModule '
    '(endpoint /health pentru monitoring). Baza de date PostgreSQL 16 este gestionată '
    'prin Prisma ORM cu migrări versionate. MqttService menține un registru in-memory de '
    'alerte (limitat la 200 intrări) populat automat la detectarea anomaliilor pe '
    'parking/diagnostics: viteză > limita configurată, temperatură > 35°C (avertisment) '
    'sau > 40°C (critic), detecție flacără (critic) sau nivel gaz > 700 (avertisment).')

subheading(doc, '3.4. Aplicația mobilă Flutter')
body(doc,
    'Aplicația Flutter (Dart 3, Flutter 3.22) suportă iOS 12+ și Android 8.0+. '
    'Utilizatorul standard dispune de patru file: cod QR personal, hartă interactivă '
    'cu 20 de locuri, istoric sesiuni cu costul calculat și profil cu preferință loc. '
    'Administratorul dispune de șase file: Dashboard (statistici timp real – locuri '
    'ocupate, rezervate, libere), Editor (configurare coordonate GPS și tarif orar), '
    'Scanner QR (camera telefonului pentru check-in/out manual), Camera (flux video live '
    'de la ESP32-CAM), Config (parametri sistem – limită viteză, praguri senzori) și '
    'Alerte (AdminAlertsScreen). AdminAlertsScreen afișează alertele cu codificare '
    'cromatică după severitate (roșu = critic, portocaliu = avertisment), refresh automat '
    'la 5 secunde și indicator de alerte necitite. Modul DirectionalNavigationScreen '
    'integrează un overlay AnimatedOpacity care se activează la depășirea limitei de '
    'viteză, afișând valoarea curentă cu indicator vizual și buton de dismiss. '
    'Autentificarea biometrică (Face ID/Touch ID) este gestionată prin flutter_local_auth, '
    'cu stocare securizată prin flutter_secure_storage.')

# ══════════════════════════════════════════════════════════════════════════
# 4. IMPLEMENTARE
# ══════════════════════════════════════════════════════════════════════════
heading(doc, '4. IMPLEMENTARE', sb=10)

subheading(doc, '4.1. Fluxul de acces prin QR și MQTT')
body(doc,
    'Fiecărui utilizator înregistrat i se generează un cod QR hexazecimal unic de 32 de '
    'caractere (128 biți entropie, imposibil de ghicit prin forță brută). Fluxul complet '
    'de intrare se desfășoară în cinci etape: (1) utilizatorul prezintă telefonul la '
    'cititorul GM65; (2) scriptul scanner_bridge.py publică codul pe topic-ul MQTT '
    'parking/entry; (3) backend-ul identifică utilizatorul, verifică absența unei sesiuni '
    'active și alocă locul optim conform preferinței configurate (cel mai aproape de '
    'intrare, de ieșire, de magazine sau un loc specific); (4) se publică comanda MQTT '
    '{"command":"OPEN_ENTRY","spot":"A3"} – ESP32-ul deschide bariera, aprinde LED-ul '
    'albastru pentru locul rezervat și actualizează LCD-ul; (5) sesiunea este înregistrată '
    'în PostgreSQL cu timestamp, utilizator și loc alocat. Întregul ciclu se finalizează '
    'în mai puțin de 400 ms. La ieșire, fluxul simetric cu comanda OPEN_EXIT finalizează '
    'sesiunea, calculează costul (tarif orar × durată în minute / 60) și îl afișează în '
    'istoricul aplicației mobile.')

figure_placeholder(doc, 2,
    'Diagrama secvență – flux complet acces QR prin MQTT.',
    height_cm=5.5)

subheading(doc, '4.2. Detecția video cu OpenCV')
body(doc,
    'Modulul detect_spots.py citește fluxul MJPEG de la ESP32-CAM și aplică algoritmul '
    'BackgroundSubtractorMOG2 (history=500, varThreshold=16) pe Regiunile de Interes '
    '(ROI) definite prin calibrare interactivă (calibrate.py). Fiecare ROI '
    '[x, y, lățime, înălțime] corespunde unui loc de parcare. Un loc este considerat '
    'ocupat dacă fracția de pixeli activi în ROI depășește pragul 0,15. Un mecanism de '
    'debouncing cu fereastră de 3 cadre consecutive previne tranzițiile false cauzate de '
    'umbre, reflexii sau artefacte video temporare. Starea fiecărui loc este publicată pe '
    'MQTT parking/sensor/{spotName} la fiecare ciclu de 5 secunde, declanșând actualizarea '
    'bazei de date și a benzii LED WS2812B.')

subheading(doc, '4.3. Funcționalități mobile cheie')
body(doc,
    'Harta interactivă a parcării afișează în timp real starea celor 20 de locuri '
    '(A1–A10, B1–B10) cu codificare cromatică verde/albastru/roșu, sincronizată la fiecare '
    '3 secunde cu backend-ul prin polling REST. La alocarea unui loc, Google Maps SDK '
    'lansează navigarea GPS pas cu pas de la locația curentă a utilizatorului până la '
    'coordonatele locului din parcare. Sesiunea activă afișează un cronometru în timp real '
    'și costul estimat calculat local. Scannerul QR integrat (pachet mobile_scanner) permite '
    'administratorului să proceseze check-in/out manual direct din interfața mobilă, fără '
    'hardware fizic. Funcția de resetare parolă folosește tokenuri expirate la 1 oră, '
    'trimise prin email cu serviciul SMTP configurat (Nodemailer).')

subheading(doc, '4.4. Securitate multistrat')
body(doc,
    'Securitatea este implementată pe cinci niveluri complementare: (1) Stocare parole '
    'exclusiv prin bcrypt cu 10 runde de salt (cost factor 2¹⁰); (2) Autentificare prin '
    'token-uri JWT semnate RS256, expirare configurabilă (implicit 24 ore), verificate la '
    'fiecare cerere prin guard-ul AuthGuard; (3) Verificare obligatorie a adresei de email '
    'la înregistrare – token hex 32B valid 24 ore, trimis prin SMTP și invalitat după '
    'utilizare; (4) Cod QR unic per utilizator cu 128 biți entropie – imposibil de forțat '
    'brut; (5) Comunicare mobilă exclusiv HTTPS; brokerul MQTT izolat în rețeaua Docker '
    'privată. Sistemul respectă principiile OWASP Top 10, inclusiv validarea strictă a '
    'intrărilor prin class-validator și CORS configurat.')

subheading(doc, '4.5. Sistem de alerte IoT și monitorizare mediu')
body(doc,
    'MqttService procesează datele primite pe parking/diagnostics și menține un registru '
    'circular in-memory de maxim 200 alerte. Fiecare alertă stochează: tipul '
    '(speed/temperature/flame/gas), severitatea (warning/critical), valoarea măsurată, '
    'descrierea și timestamp-ul ISO 8601. Pragurile de alertare: viteză > limita din '
    'ParkingConfig (implicit 10 km/h), temperatură > 35°C (avertisment) sau > 40°C '
    '(critic), detecție flacără = critic (prioritate maximă), nivel gaz > 700 unități '
    'analogice = avertisment. Trei endpoint-uri REST dedicate: GET /parking/alerts '
    '(lista alertelor + câmpul unreadCount), POST /parking/alerts/read (resetare contor '
    'alerte necitite) și POST /parking/alerts/mock (populare cu 6 alerte de test pentru '
    'development). La primirea oricărei alerte de tip critic, ESP32-ul primește comanda '
    'MQTT de activare a benzii LED WS2812B în modul de urgență (pulsare roșie la 2 Hz).')

# ══════════════════════════════════════════════════════════════════════════
# 5. REZULTATE EXPERIMENTALE
# ══════════════════════════════════════════════════════════════════════════
heading(doc, '5. REZULTATE EXPERIMENTALE', sb=10)
body(doc,
    'Sistemul a fost testat pe un prototip fizic funcțional reprezentând o parcare cu '
    '4 locuri fizice, scalată prin configurație la 20 de locuri logice (A1–A10, B1–B10). '
    'Testele de performanță s-au desfășurat pe o rețea Wi-Fi 2,4 GHz, pe durata a 72 de '
    'ore de funcționare continuă. Tabelul 1 sintetizează principalii indicatori măsurați.')

para(doc, '', sb=4, sa=2)
add_results_table(doc)

p_tbl_cap = doc.add_paragraph()
set_para_fmt(p_tbl_cap, align=WD_ALIGN_PARAGRAPH.CENTER, sb=3, sa=8)
r_tbl_cap = p_tbl_cap.add_run('Tabelul 1. Indicatori de performanță măsurați pe prototip.')
set_font(r_tbl_cap, size=9, italic=True)

body(doc,
    'Latența de 320 ms de la scanare la deschiderea barierei se compune din: transmisie '
    'USB HID cititor → PC (< 50 ms), procesare cerere REST în backend (~80 ms), publicare '
    'și recepție mesaj MQTT (~60 ms) și acționare fizică servomotor (~130 ms). Precizia '
    'de 97,3% a detecției OpenCV a fost evaluată pe 300 de capturi cu ocupare cunoscută, '
    'în condiții variate de iluminare. Principala sursă de eroare (2,7%) a constituit-o '
    'reflexia farurilor vehiculelor pe pardoseala lucioasă în condiții de lumină directă. '
    'Sistemul de alerte IoT a detectat 100% din evenimentele de flacără simulate și 98,5% '
    'din depășirile de viteză înregistrate în sesiunile de test.')

# ══════════════════════════════════════════════════════════════════════════
# 6. CONCLUZII
# ══════════════════════════════════════════════════════════════════════════
heading(doc, '6. CONCLUZII', sb=10)
body(doc,
    'Lucrarea prezintă un sistem funcțional și validat de parcare inteligentă ce integrează '
    'hardware IoT, procesare video, comunicare în timp real prin MQTT și o aplicație mobilă '
    'modernă cross-platform. Arhitectura distribuită, bazată exclusiv pe tehnologii '
    'open-source, asigură scalabilitate orizontală și independență față de furnizori. '
    'Contribuțiile originale ale lucrării includ: (1) integrarea completă a lanțului '
    'hardware–software de la senzor la aplicația mobilă; (2) subsistemul de alerte IoT cu '
    'monitorizare a 6 tipuri de senzori în timp real; (3) banda LED WS2812B ca interfață '
    'vizuală sincronizată cu starea locurilor; (4) navigarea GPS internă cu overlay de '
    'alertă viteză în DirectionalNavigationScreen; (5) panoul AdminAlertsScreen cu refresh '
    'automat și prioritizare cromatică a alertelor.')
body(doc,
    'Rezultatele experimentale confirmă funcționabilitatea sistemului: latență end-to-end '
    'de 320 ms, precizie video de 97,3% și uptime de 100% pe o perioadă de testare de '
    '72 ore. Direcțiile viitoare de cercetare includ: (1) navigare GIS indoor cu integrarea '
    'hărții 3D a parcării; (2) predicția ocupării prin algoritmi de machine learning pe date '
    'istorice; (3) integrarea plății mobile prin NFC sau cod QR dinamic; (4) extinderea la '
    'arhitecturi multi-parcare cu centralizare în cloud.')

# ── MULȚUMIRI ────────────────────────────────────────────────────────────────
heading(doc, 'MULȚUMIRI', sb=10)
body(doc,
    'Autorul mulțumește conducătorului științific Asist. Univ. Drd. Ing. Silvian-Marian '
    'Petrică pentru îndrumarea continuă pe parcursul elaborării acestei lucrări, precum și '
    'colegilor din Facultatea Hidrotehnica – specializarea Automatică și Informatică '
    'Aplicată pentru suportul tehnic acordat în faza de testare a prototipului fizic.')

# ── BIBLIOGRAFIE ──────────────────────────────────────────────────────────────
heading(doc, 'BIBLIOGRAFIE', sb=10)
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
    para(doc, ref, size=10, sa=2, left_indent=Cm(0.5))

# ─── Salvare ─────────────────────────────────────────────────────────────────
doc.save(OUT)
print(f'✓ Lucrare salvată: {OUT}')
