"""
Generator SRS – format academic standard românesc (lucrare de licență)
Times New Roman 12pt, rânduri la 1.5, justify, margini standard, fără tabele.
"""
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

FONT = 'Times New Roman'
SB   = Pt(12)   # size body
SH1  = Pt(14)
SH2  = Pt(13)
SH3  = Pt(12)

doc = Document()
sec = doc.sections[0]
sec.left_margin   = Cm(3.0)
sec.right_margin  = Cm(2.0)
sec.top_margin    = Cm(2.5)
sec.bottom_margin = Cm(2.5)

sn = doc.styles['Normal']
sn.font.name = FONT
sn.font.size = SB
sn.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
sn.paragraph_format.space_after  = Pt(0)
sn.paragraph_format.space_before = Pt(0)

for name, sz in [('Heading 1', SH1), ('Heading 2', SH2), ('Heading 3', SH3)]:
    s = doc.styles[name]
    s.font.name = FONT; s.font.size = sz; s.font.bold = True
    s.font.color.rgb = RGBColor(0, 0, 0)
    s.paragraph_format.space_before = Pt(18); s.paragraph_format.space_after = Pt(6)
    s.paragraph_format.keep_with_next = True
    s.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE

# ── Header cu tabel 1 rând × 2 coloane (fără borduri) ────────────────────────
sec.header.is_linked_to_previous = False
# goalește paragraful implicit din header
hp0 = sec.header.paragraphs[0]
hp0.text = ''
hp0.paragraph_format.space_after  = Pt(0)
hp0.paragraph_format.space_before = Pt(0)

# tabel 1x2 fără borduri vizibile
htbl = sec.header.add_table(rows=1, cols=2, width=Cm(16))
htbl.style = 'Table Grid'
# eliminăm bordurile tabelului din header
from docx.oxml import OxmlElement as _OE
tblPr = htbl._tbl.tblPr
tblBdr = _OE('w:tblBorders')
for side in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
    b = _OE(f'w:{side}')
    b.set(qn('w:val'), 'none')
    b.set(qn('w:sz'), '0')
    b.set(qn('w:space'), '0')
    b.set(qn('w:color'), 'auto')
    tblBdr.append(b)
tblPr.append(tblBdr)

# celula stânga – instituție
cl = htbl.cell(0, 0)
cl.width = Cm(10)
pl = cl.paragraphs[0]
pl.alignment = WD_ALIGN_PARAGRAPH.LEFT
pl.paragraph_format.space_after  = Pt(0)
pl.paragraph_format.space_before = Pt(0)
rl = pl.add_run('Universitatea Tehnică de Construcții București')
rl.font.name = FONT; rl.font.size = Pt(9); rl.italic = True

# celula dreapta – titlu document
cr = htbl.cell(0, 1)
cr.width = Cm(6)
pr = cr.paragraphs[0]
pr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
pr.paragraph_format.space_after  = Pt(0)
pr.paragraph_format.space_before = Pt(0)
rr = pr.add_run('SRS – Sistem de Parcare Inteligentă')
rr.font.name = FONT; rr.font.size = Pt(9); rr.italic = True

# linie orizontală sub tabel (border bottom pe ultimul paragraf al header-ului)
def _add_bottom_border(p):
    pPr = p._p.get_or_add_pPr()
    pBdr = _OE('w:pBdr')
    btm = _OE('w:bottom')
    btm.set(qn('w:val'), 'single'); btm.set(qn('w:sz'), '6')
    btm.set(qn('w:space'), '1');   btm.set(qn('w:color'), '000000')
    pBdr.append(btm); pPr.append(pBdr)

_add_bottom_border(pr)
_add_bottom_border(pl)

# ── Footer: – număr – centrat ────────────────────────────────────────────────
sec.footer.is_linked_to_previous = False
fp = sec.footer.paragraphs[0]
fp.clear()
fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
fp.paragraph_format.space_before = Pt(4)
fp.paragraph_format.space_after  = Pt(0)

f_run0 = fp.add_run('– ')
f_run0.font.name = FONT; f_run0.font.size = Pt(10)

f_run1 = fp.add_run()
f_run1.font.name = FONT; f_run1.font.size = Pt(10)
fc_begin = _OE('w:fldChar'); fc_begin.set(qn('w:fldCharType'), 'begin')
f_run1._r.append(fc_begin)

f_run2 = fp.add_run()
f_run2.font.name = FONT; f_run2.font.size = Pt(10)
f_instr = _OE('w:instrText'); f_instr.set(qn('xml:space'), 'preserve'); f_instr.text = ' PAGE '
f_run2._r.append(f_instr)

f_run3 = fp.add_run()
f_run3.font.name = FONT; f_run3.font.size = Pt(10)
fc_end = _OE('w:fldChar'); fc_end.set(qn('w:fldCharType'), 'end')
f_run3._r.append(fc_end)

f_run4 = fp.add_run(' –')
f_run4.font.name = FONT; f_run4.font.size = Pt(10)


def h(text, level=1):
    p = doc.add_heading(text, level=level)
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for r in p.runs:
        r.font.name = FONT; r.font.color.rgb = RGBColor(0, 0, 0)


def para(text, fi=True):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    p.paragraph_format.space_after = Pt(8); p.paragraph_format.space_before = Pt(0)
    if fi:
        p.paragraph_format.first_line_indent = Cm(1.25)
    r = p.add_run(text); r.font.name = FONT; r.font.size = SB
    return p


def bul(text):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.left_indent = Cm(1.0)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    p.paragraph_format.space_after = Pt(3); p.paragraph_format.space_before = Pt(0)
    r = p.add_run(text); r.font.name = FONT; r.font.size = SB
    return p


def lbl(label, text):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    p.paragraph_format.first_line_indent = Cm(1.25)
    p.paragraph_format.space_after = Pt(3); p.paragraph_format.space_before = Pt(0)
    r1 = p.add_run(label + ': '); r1.bold = True; r1.font.name = FONT; r1.font.size = SB
    r2 = p.add_run(text); r2.font.name = FONT; r2.font.size = SB
    return p


_cur_req_tbl = [None]

def new_req_table():
    """Creează tabel nou cu header pentru cerințe funcționale (Cod | Prioritate | Descriere)."""
    from docx.oxml import OxmlElement as _OE3
    tbl = doc.add_table(rows=1, cols=3)
    tbl.style = 'Table Grid'
    # Lățimi: 2.2cm | 2.5cm | 11.3cm = 16cm
    hrow = tbl.rows[0]
    for i, (label, w) in enumerate([('Cod', Cm(2.2)), ('Prioritate', Cm(2.5)), ('Descriere', Cm(11.3))]):
        cell = hrow.cells[i]
        cell.width = w
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after  = Pt(3)
        r = p.add_run(label)
        r.bold = True; r.font.name = FONT; r.font.size = Pt(11)
        tcPr = cell._tc.get_or_add_tcPr()
        shd = _OE3('w:shd')
        shd.set(qn('w:val'), 'clear')
        shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'), 'D9D9D9')
        tcPr.append(shd)
    _cur_req_tbl[0] = tbl


def rq(rid, prio, text):
    tbl = _cur_req_tbl[0]
    row = tbl.add_row()
    cells = row.cells
    # Cod
    p0 = cells[0].paragraphs[0]
    p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p0.paragraph_format.space_before = Pt(3); p0.paragraph_format.space_after = Pt(3)
    r0 = p0.add_run(rid); r0.bold = True; r0.font.name = FONT; r0.font.size = Pt(10)
    # Prioritate
    p1 = cells[1].paragraphs[0]
    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p1.paragraph_format.space_before = Pt(3); p1.paragraph_format.space_after = Pt(3)
    color_map = {
        'Critic': RGBColor(0xC0, 0x00, 0x00),
        'Înalt':  RGBColor(0xFF, 0x66, 0x00),
        'Mediu':  RGBColor(0x00, 0x70, 0xC0),
        'Redus':  RGBColor(0x00, 0x70, 0x00),
    }
    r1 = p1.add_run(prio); r1.bold = True; r1.font.name = FONT; r1.font.size = Pt(10)
    r1.font.color.rgb = color_map.get(prio, RGBColor(0, 0, 0))
    # Descriere
    p2 = cells[2].paragraphs[0]
    p2.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p2.paragraph_format.space_before = Pt(3); p2.paragraph_format.space_after = Pt(3)
    p2.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    r2 = p2.add_run(text); r2.font.name = FONT; r2.font.size = Pt(10)


def cp(text, sz=12, bold=False, sb=0, sa=6):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(sb); p.paragraph_format.space_after = Pt(sa)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    r = p.add_run(text); r.bold = bold; r.font.name = FONT; r.font.size = Pt(sz)
    return p


# ═══════════════════════════════════════════════════════════════════════════
# PAGINA DE TITLU
# ═══════════════════════════════════════════════════════════════════════════
cp('UNIVERSITATEA TEHNICĂ DE CONSTRUCȚII BUCUREȘTI', 13, bold=True, sb=36, sa=6)
cp('Facultatea de Electronică, Telecomunicații și Tehnologia Informației', 12, sa=6)
cp('Departamentul de Ingineria Sistemelor', 12, sa=48)
cp('DOCUMENT DE SPECIFICARE A CERINȚELOR SOFTWARE', 16, bold=True, sb=24, sa=12)
cp('(Software Requirements Specification – SRS)', 13, sa=12)
cp('Sistem de Parcare Inteligentă – Smart Parking', 14, bold=True, sa=60)
cp('Versiunea 1.0', 12, sa=6)
cp('București, 2026', 12)
doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════
# CUPRINS
# ═══════════════════════════════════════════════════════════════════════════
h('Cuprins', level=1)
items = [
    ('1. Introducere', False),
    ('1.1. Scopul documentului', True),
    ('1.2. Scopul produsului', True),
    ('1.3. Definiții, acronime și abrevieri', True),
    ('1.4. Referințe', True),
    ('1.5. Prezentare generală a documentului', True),
    ('2. Descrierea generală', False),
    ('2.1. Perspectiva produsului', True),
    ('2.2. Funcțiile principale ale produsului', True),
    ('2.3. Caracteristicile utilizatorilor', True),
    ('2.4. Constrângeri generale', True),
    ('2.5. Ipoteze și dependențe', True),
    ('3. Cerințe funcționale', False),
    ('3.1. Autentificare și gestionarea conturilor', True),
    ('3.2. Generare și scanare cod QR', True),
    ('3.3. Gestionarea locurilor de parcare', True),
    ('3.4. Sesiuni de parcare', True),
    ('3.5. Navigare GPS', True),
    ('3.6. Funcționalități specifice administratorului', True),
    ('3.7. Comunicare MQTT și integrare IoT', True),
    ('3.8. Detecție video a ocupării locurilor', True),
    ('4. Cerințe non-funcționale', False),
    ('4.1. Performanță', True),
    ('4.2. Securitate', True),
    ('4.3. Fiabilitate', True),
    ('4.4. Portabilitate și mentenabilitate', True),
    ('5. Cerințe de interfață externă', False),
    ('5.1. Interfața cu utilizatorul', True),
    ('5.2. Interfața hardware', True),
    ('5.3. Interfața software', True),
    ('5.4. Interfața de comunicare', True),
    ('6. Alte cerințe', False),
    ('6.1. Cerințe de instalare și configurare', True),
    ('6.2. Cerințe de documentare', True),
    ('6.3. Cerințe de scalabilitate', True),
]
for title, is_sub in items:
    p = doc.add_paragraph()
    p.paragraph_format.space_after  = Pt(2); p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    p.paragraph_format.left_indent  = Cm(1.25 if is_sub else 0)
    run = p.add_run(title); run.font.name = FONT; run.font.size = Pt(12)
    run.bold = not is_sub
doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════
# 1. INTRODUCERE
# ═══════════════════════════════════════════════════════════════════════════
h('1. Introducere', level=1)

h('1.1. Scopul documentului', level=2)
para(
    'Prezentul document constituie Specificarea Cerințelor Software (Software Requirements '
    'Specification – SRS) pentru sistemul de parcare inteligentă Smart Parking, elaborat '
    'în conformitate cu standardul IEEE 830-1998. Documentul descrie cerințele funcționale '
    'și non-funcționale ale sistemului, servind ca bază de acord între echipa de dezvoltare '
    'și beneficiarii proiectului, precum și ca referință pe toată durata ciclului de viață '
    'al software-ului.'
)

h('1.2. Scopul produsului', level=2)
para(
    'Smart Parking este un sistem integrat de gestiune a parcărilor care îmbină hardware IoT, '
    'comunicare în timp real și o aplicație mobilă modernă. Sistemul permite utilizatorilor '
    'să rezerve locuri de parcare, să acceseze parcarea prin coduri QR personalizate și să '
    'navigheze cu GPS până la locul alocat. Administratorii dispun de un panou de control '
    'centralizat pentru monitorizarea și administrarea întregii infrastructuri.'
)
para(
    'Principalele beneficii constau în reducerea timpului de căutare a unui loc disponibil, '
    'securizarea accesului prin coduri QR unice, monitorizarea în timp real a ocupării, '
    'navigarea asistată GPS și administrarea centralizată. Sistemul include, de asemenea, '
    'autentificare biometrică (Face ID / Touch ID) pentru un acces rapid și securizat pe '
    'dispozitivele mobile compatibile.'
)

h('1.3. Definiții, acronime și abrevieri', level=2)
para('În cuprinsul acestui document sunt utilizați următorii termeni tehnici și abrevieri:')
lbl('SRS', 'Software Requirements Specification – Document de Specificare a Cerințelor Software')
lbl('IoT', 'Internet of Things – rețeaua de dispozitive fizice conectate la internet')
lbl('MQTT', 'Message Queuing Telemetry Transport – protocol ușor de comunicare publish/subscribe pentru IoT')
lbl('QR Code', 'Quick Response Code – cod de bare bidimensional utilizat pentru acces rapid prin scanare')
lbl('ESP32', 'microcontroler cu Wi-Fi și Bluetooth integrat, produs de Espressif Systems')
lbl('API', 'Application Programming Interface – interfață de programare pentru comunicarea între componente software')
lbl('REST', 'Representational State Transfer – stil arhitectural pentru servicii web bazate pe HTTP')
lbl('JWT', 'JSON Web Token – standard deschis (RFC 7519) pentru transmiterea securizată a informațiilor')
lbl('GPS', 'Global Positioning System – sistem de navigare prin satelit ce furnizează localizarea geografică')
lbl('ORM', 'Object-Relational Mapping – mapare a obiectelor din cod la structuri relaționale din baza de date')
lbl('ROI', 'Region of Interest – regiune de interes în cadrul unui cadru video pentru analiza imaginilor')
lbl('NestJS', 'framework Node.js pentru construirea aplicațiilor server-side scalabile, bazat pe TypeScript')
lbl('Flutter', 'framework Google pentru dezvoltarea aplicațiilor mobile cross-platform dintr-o singură bază de cod')
lbl('Prisma', 'ORM modern pentru Node.js și TypeScript, cu migrări automate și client tipizat')
lbl('Docker', 'platformă de containerizare ce permite rularea aplicațiilor în medii izolate și reproductibile')
lbl('PostgreSQL', 'sistem de gestiune a bazelor de date relaționale open-source')
lbl('bcrypt', 'funcție de hash criptografic concepută pentru stocarea securizată a parolelor')

h('1.4. Referințe', level=2)
para(
    'Documentul a fost elaborat cu referire la următoarele surse: [1] IEEE Std 830-1998 – '
    'IEEE Recommended Practice for Software Requirements Specifications; [2] NestJS '
    'Documentation, documentație oficială la https://docs.nestjs.com; [3] Flutter '
    'Documentation, documentație oficială la https://docs.flutter.dev; [4] Prisma '
    'Documentation, documentație oficială la https://www.prisma.io/docs; [5] Eclipse '
    'Mosquitto, documentație oficială la https://mosquitto.org; [6] ESP32 Technical '
    'Reference Manual, Espressif Systems; [7] OpenCV Documentation, documentație '
    'oficială la https://docs.opencv.org; [8] RFC 7519 – JSON Web Token (JWT), '
    'Internet Engineering Task Force, 2015.'
)

h('1.5. Prezentare generală a documentului', level=2)
para(
    'Documentul este structurat în șase secțiuni principale. Secțiunea 2 oferă o descriere '
    'generală a sistemului. Secțiunea 3 detaliază cerințele funcționale, organizate pe opt '
    'module tematice. Secțiunea 4 prezintă cerințele non-funcționale. Secțiunea 5 descrie '
    'interfețele externe, iar Secțiunea 6 cuprinde alte cerințe relevante.'
)
doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════
# 2. DESCRIEREA GENERALĂ
# ═══════════════════════════════════════════════════════════════════════════
h('2. Descrierea generală', level=1)

h('2.1. Perspectiva produsului', level=2)
para(
    'Smart Parking este un sistem nou, de sine stătător, care nu depinde de alte sisteme '
    'software preexistente. Sistemul integrează mai multe subsisteme interconectate printr-o '
    'arhitectură distribuită: subsistemul hardware bazat pe microcontrolere ESP32 (senzori '
    'de ocupare, servomotoare pentru bariere, cameră IP), subsistemul de detecție video '
    'implementat în Python cu OpenCV, subsistemul backend NestJS cu baza de date PostgreSQL '
    'gestionată prin Prisma și subsistemul mobil Flutter pentru utilizatori și administratori.'
)
para(
    'Singura dependență externă semnificativă o reprezintă serviciul Google Maps, utilizat '
    'pentru cartografiere și navigare GPS. Toate celelalte componente funcționează exclusiv '
    'în rețeaua locală, fără conectivitate externă continuă.'
)

h('2.2. Funcțiile principale ale produsului', level=2)
para(
    'Funcțiile destinate utilizatorilor finali cuprind: înregistrarea în sistem prin email '
    'și parolă cu verificare obligatorie a adresei; autentificarea prin email/parolă sau '
    'prin metode biometrice (Face ID / Touch ID); generarea unui cod QR unic utilizat ca '
    'acreditare de acces; vizualizarea în timp real a hărții interactive a parcării cu '
    'cele 20 de locuri color-codificate; alocarea automată a unui loc conform preferinței '
    'configurate; navigarea GPS pas cu pas de la locația curentă până la locul alocat; '
    'accesul prin bariera de intrare prin prezentarea codului QR la scannerul fizic; '
    'vizualizarea sesiunii active și a istoricului sesiunilor cu durată și cost calculat.'
)
para(
    'Funcțiile destinate administratorilor cuprind: accesul la un dashboard în timp real '
    'cu situația tuturor locurilor și sesiunilor active; scanarea manuală a codurilor QR '
    'prin camera telefonului; deschiderea manuală a barierelor (BYPASS) în situații de '
    'urgență; editarea configurației globale a parcării – tarif orar, limită de viteză, '
    'coordonate GPS; vizualizarea fluxului video live de la camera de supraveghere.'
)

h('2.3. Caracteristicile utilizatorilor', level=2)
para(
    'Sistemul deservește trei categorii de utilizatori cu niveluri tehnice diferite. '
    'Utilizatorul final este o persoană care dorește să parcheaze, fără cunoștințe tehnice '
    'speciale. Interfața mobilă este concepută pentru simplitate, astfel încât orice '
    'persoană familiarizată cu un smartphone să poată opera sistemul fără instruire.'
)
para(
    'Administratorul este persoana responsabilă de gestionarea parcării, cu un nivel tehnic '
    'mediu, suficient pentru utilizarea interfeței de administrare. Operatorul tehnic '
    'instalează și menține componentele hardware și necesită cunoștințe avansate de '
    'electronică, programare C++/Arduino și rețelistică Wi-Fi.'
)

h('2.4. Constrângeri generale', level=2)
para(
    'Aplicația mobilă este compatibilă cu iOS 12 și versiuni superioare, respectiv Android '
    '8.0 (API nivel 26) și versiuni superioare. Serverul backend necesită Node.js 18 sau '
    'mai recent și PostgreSQL 16. Componentele ESP32 necesită o rețea Wi-Fi de 2,4 GHz '
    'funcțională. Modulul de detecție video necesită o cameră cu rezoluție minimă de 720p. '
    'Configurația curentă suportă maximum 20 de locuri (A1–A10, B1–B10). Brokerul MQTT '
    'Mosquitto trebuie să fie accesibil pe portul 1883 al rețelei locale.'
)

h('2.5. Ipoteze și dependențe', level=2)
para(
    'Utilizatorii dețin un smartphone cu cameră funcțională. Rețeaua Wi-Fi locală este '
    'stabilă și disponibilă permanent. Serviciul Google Maps API este disponibil, cu o '
    'cheie API validă configurată. Serverul Docker dispune de minimum 4 GB RAM. Codurile '
    'QR sunt considerate confidențiale; sistemul nu răspunde pentru partajarea lor de '
    'către utilizatori.'
)
doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════
# 3. CERINȚE FUNCȚIONALE
# ═══════════════════════════════════════════════════════════════════════════
h('3. Cerințe funcționale', level=1)
para(
    'Cerințele funcționale sunt organizate pe opt module. Fiecare cerință este identificată '
    'printr-un cod [CF-XXX] urmat de prioritatea sa: Critic, Înalt, Mediu sau Redus.'
)

h('3.1. Autentificare și gestionarea conturilor', level=2)
new_req_table()
rq('CF-001', 'Critic',
    'Sistemul permite înregistrarea unui utilizator nou pe baza adresei de email și a parolei. '
    'Parola este stocată exclusiv criptată cu bcrypt (10 runde de salt). Nicio componentă '
    'nu stochează parola în text clar.')
rq('CF-002', 'Critic',
    'La înregistrare, sistemul trimite automat un email de verificare la adresa furnizată, '
    'cu un link conținând un token unic (hex 32 octeți). Contul devine activ doar după '
    'accesarea link-ului.')
rq('CF-003', 'Critic',
    'La autentificarea cu succes, serverul returnează un token JWT utilizat pentru '
    'autorizarea tuturor cererilor ulterioare. Token-urile expirate sunt respinse cu '
    'codul HTTP 401.')
rq('CF-004', 'Înalt',
    'Sistemul suportă autentificarea biometrică (Face ID / Touch ID) pe dispozitivele '
    'compatibile, prin Flutter Local Auth cu stocare securizată în Keychain (iOS) / '
    'Keystore (Android).')
rq('CF-005', 'Înalt',
    'Utilizatorul poate solicita resetarea parolei printr-un link trimis pe email. '
    'Token-ul de resetare are valabilitate de o oră, după care este invalidat automat.')
rq('CF-006', 'Mediu',
    'Utilizatorul poate actualiza culoarea mașinii sale din profilul aplicației, '
    'pentru identificarea vizuală a vehiculului.')
rq('CF-007', 'Înalt',
    'Utilizatorul poate seta preferința de parcare: loc specific (A1–B10), cel mai '
    'apropiat de intrare, de ieșire sau de zona de magazine.')
rq('CF-008', 'Critic',
    'Sistemul gestionează rolurile "user" și "admin", fiecare cu funcționalități și '
    'ecrane dedicate în aplicația mobilă.')

h('3.2. Generare și scanare cod QR', level=2)
new_req_table()
rq('CF-009', 'Critic',
    'Fiecare utilizator primește un cod QR unic la primul login, ca șir hexazecimal de '
    '16 octeți (32 de caractere), garantat unic prin verificare prealabilă în baza de date.')
rq('CF-010', 'Critic',
    'Codul QR este afișat permanent pe prima filă a aplicației mobile, disponibil '
    'oricând pentru prezentare la bariera de acces.')
rq('CF-011', 'Critic',
    'Scannerul hardware GM65 (USB HID) trimite codul citit pe topic-ul MQTT parking/scan '
    'sau la endpoint-ul /parking/hardware-scan, iar backend-ul procesează cererea automat.')
rq('CF-012', 'Critic',
    'La scanarea la intrare, sistemul identifică utilizatorul, alocă cel mai potrivit '
    'loc disponibil și deschide bariera de intrare prin comanda MQTT OPEN_ENTRY.')
rq('CF-013', 'Critic',
    'La scanarea la ieșire, sistemul identifică sesiunea activă, o încheie, calculează '
    'costul și deschide bariera de ieșire prin comanda MQTT OPEN_EXIT.')
rq('CF-014', 'Înalt',
    'Aplicația administratorului permite scanarea codurilor QR prin camera telefonului, '
    'ca alternativă la scannerul fizic.')

h('3.3. Gestionarea locurilor de parcare', level=2)
new_req_table()
rq('CF-015', 'Critic',
    'Sistemul gestionează 20 de locuri (A1–A10, B1–B10), fiecare cu coordonate GPS '
    'individuale pentru navigarea precisă.')
rq('CF-016', 'Critic',
    'Fiecare loc are o stare: disponibil, ocupat sau rezervat. Tranzițiile sunt '
    'gestionate exclusiv de server pe baza evenimentelor primite.')
rq('CF-017', 'Critic',
    'Starea locurilor se actualizează în timp real pe baza mesajelor MQTT de la '
    'senzorii fizici ESP32 sau de la modulul de detecție video Python.')
rq('CF-018', 'Înalt',
    'Harta interactivă afișează locurile color-codificate: verde (disponibil), '
    'roșu (ocupat), albastru (alocat utilizatorului curent).')
rq('CF-019', 'Critic',
    'Alocarea unui loc se realizează printr-o tranzacție atomică Prisma ($transaction) '
    'pentru a preveni conflictele la cereri simultane.')
rq('CF-020', 'Mediu',
    'Administratorul poate crea, actualiza și șterge locuri, precum și edita '
    'coordonatele GPS ale fiecăruia.')

h('3.4. Sesiuni de parcare', level=2)
new_req_table()
rq('CF-021', 'Critic',
    'La check-in se creează o sesiune cu identificatorul utilizatorului, '
    'identificatorul locului alocat și startTime = momentul curent.')
rq('CF-022', 'Critic',
    'La check-out sesiunea se actualizează cu endTime = momentul curent, '
    'marcând finalizarea parcării.')
rq('CF-023', 'Înalt',
    'Costul se calculează automat: durată (ore) × tarif orar din configurația parcării.')
rq('CF-024', 'Înalt',
    'Utilizatorul poate vizualiza istoricul sesiunilor proprii cu detalii despre '
    'locul utilizat, data, durata și costul.')
rq('CF-025', 'Înalt',
    'Aplicația afișează în timp real sesiunea activă (locul alocat, timpul scurs) '
    'prin interogare periodică la fiecare 3 secunde.')
rq('CF-026', 'Mediu',
    'Administratorul poate vizualiza istoricul complet al tuturor sesiunilor.')

h('3.5. Navigare GPS', level=2)
new_req_table()
rq('CF-027', 'Înalt',
    'Imediat după check-in, aplicația redirecționează la ecranul de navigare GPS cu '
    'o polilinie pe Google Maps de la locația curentă până la locul alocat.')
rq('CF-028', 'Înalt',
    'Navigarea utilizează localizarea GPS curentă ca punct de start. Permisiunea '
    'de localizare este solicitată la prima utilizare.')
rq('CF-029', 'Mediu',
    'Harta suportă un overlay grafic al planului parcării suprapus pe harta satelitară.')
rq('CF-030', 'Mediu',
    'Ecranul afișează distanța estimată și direcția până la locul alocat, '
    'actualizate pe măsura deplasării.')

h('3.6. Funcționalități specifice administratorului', level=2)
new_req_table()
rq('CF-031', 'Critic',
    'Administratorul are acces la un dashboard în timp real cu starea tuturor locurilor, '
    'numărul de sesiuni active și lista utilizatorilor din parcare.')
rq('CF-032', 'Înalt',
    'Administratorul poate deschide manual oricare barieră prin butoanele BYPASS, '
    'independent de scanarea unui cod QR.')
rq('CF-033', 'Înalt',
    'Administratorul poate edita configurația globală: coordonate GPS pentru intrare, '
    'ieșire și magazine, tarif orar și limita de viteză.')
rq('CF-034', 'Mediu',
    'Administratorul are acces la fluxul video live de la camera de supraveghere, '
    'vizibil direct din aplicație.')
rq('CF-035', 'Înalt',
    'Administratorul poate efectua check-in și check-out manual prin scanarea '
    'codurilor QR cu camera telefonului.')

h('3.7. Comunicare MQTT și integrare IoT', level=2)
new_req_table()
rq('CF-036', 'Critic',
    'La pornire, backend-ul se conectează la brokerul MQTT și se abonează la: '
    'parking/sensor/+, parking/scan, parking/environment, parking/speed, parking/diagnostics.')
rq('CF-037', 'Critic',
    'La primirea unui mesaj pe parking/sensor/{spotName}, serverul actualizează starea '
    'locului în baza de date și publică starea completă pe parking/status.')
rq('CF-038', 'Critic',
    'La primirea unui cod QR pe parking/scan, serverul procesează check-in sau check-out '
    'și publică comanda de deschidere a barierei pe parking/commands.')
rq('CF-039', 'Mediu',
    'Serverul procesează datele de mediu (temperatură, umiditate, presiune, flacără) '
    'și datele de viteză primite de la senzori.')
rq('CF-040', 'Redus',
    'Backend-ul menține un jurnal MQTT accesibil prin /parking/mqtt-log, '
    'util pentru diagnosticare și depanare.')

h('3.8. Detecție video a ocupării locurilor', level=2)
new_req_table()
rq('CF-041', 'Înalt',
    'Modulul Python cu OpenCV analizează continuu fluxul video și determină ocuparea '
    'locurilor prin subtracție de fundal (BackgroundSubtractorMOG2).')
rq('CF-042', 'Înalt',
    'Detecția este stabilizată prin debouncing: o schimbare de stare este confirmată '
    'doar după minimum 3 cadre consecutive, pentru a evita semnalele false.')
rq('CF-043', 'Înalt',
    'Pragul de ocupare (implicit 15% din pixelii ROI activi) este configurabil în '
    'fișierul config.json.')
rq('CF-044', 'Înalt',
    'Rezultatele detecției sunt publicate pe parking/sensor/{spotName}, '
    'integrându-se transparent cu restul sistemului.')
rq('CF-045', 'Mediu',
    'Instrumentul calibrate.py permite configurarea regiunilor de interes (ROI) '
    'pentru fiecare loc, adaptând sistemul geometriei parcării.')
doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════
# 4. CERINȚE NON-FUNCȚIONALE
# ═══════════════════════════════════════════════════════════════════════════
h('4. Cerințe non-funcționale', level=1)

h('4.1. Performanță', level=2)
para(
    'Sistemul trebuie să asigure actualizarea stării locurilor cu o latență maximă de o '
    'secundă de la detectarea unui eveniment IoT, datorită caracterului asincron al '
    'protocolului MQTT. Endpoint-urile REST trebuie să răspundă în mai puțin de 200 de '
    'milisecunde pentru operațiunile standard. Intervalul de polling al aplicației mobile '
    'pentru sesiunea activă este de 3 secunde. Sistemul trebuie să suporte minimum '
    '50 de utilizatori concurenți, cu un uptime de minimum 99,5%.'
)

h('4.2. Securitate', level=2)
para(
    'Parolele sunt stocate exclusiv prin hash bcrypt cu 10 runde de salt, nicio componentă '
    'neexpunând parola în text clar. Toate endpoint-urile protejate verifică un token JWT '
    'valid; token-urile expirate sunt respinse cu HTTP 401. Credențialele mobile sunt '
    'stocate exclusiv prin Flutter Secure Storage (Keychain pe iOS, Keystore pe Android). '
    'Token-urile de resetare expiră după o oră. Codurile QR au 64 de biți de entropie, '
    'practic imposibil de ghicit. CORS este configurat pentru a restricționa originile '
    'admise. Sistemul respectă principiile OWASP Top 10 pentru aplicații web.'
)

h('4.3. Fiabilitate', level=2)
para(
    'Clientul MQTT implementează reconectare automată în caz de deconectare. Alocările '
    'de locuri se realizează în tranzacții atomice, prevenind alocarea dublă. Aplicația '
    'mobilă gestionează erorile de rețea cu mesaje descriptive. Containerele Docker '
    'repornesc automat (restart: unless-stopped). Endpoint-ul /health permite '
    'monitorizarea externă a stării serverului.'
)

h('4.4. Portabilitate și mentenabilitate', level=2)
para(
    'Aplicația Flutter generează cod nativ pentru iOS și Android dintr-o singură bază '
    'de cod Dart. Backend-ul containerizat Docker poate fi deployed pe orice infrastructură '
    'fără modificări. Migrările Prisma asigură versionarea controlată a schemei. '
    'Codul TypeScript tipizat reduce erorile de runtime, iar arhitectura modulară NestJS '
    'permite adăugarea de funcționalități fără a afecta modulele existente.'
)
doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════
# 5. CERINȚE DE INTERFAȚĂ EXTERNĂ
# ═══════════════════════════════════════════════════════════════════════════
h('5. Cerințe de interfață externă', level=1)

h('5.1. Interfața cu utilizatorul', level=2)
para(
    'Aplicația mobilă Flutter este interfața principală cu utilizatorul. Include ecrane de '
    'autentificare (Login, Înregistrare, Recuperare parolă, Resetare parolă), un navigator '
    'cu file pentru utilizatorul standard (QR Code, Hartă parcare, Istoric, Profil) și '
    'unul extins pentru administrator (Dashboard, Editor, Scanner QR, Camera, Istoric, '
    'Info). Interfața este responsivă, cu codificare cromatică consistentă (verde, roșu, '
    'albastru) și mesaje de eroare în limbaj accesibil.'
)

h('5.2. Interfața hardware', level=2)
para(
    'Microcontrolerele ESP32 utilizează MQTT prin Wi-Fi (2,4 GHz). Servomotoarele sunt '
    'controlate prin semnale PWM pe pinii GPIO. Senzorii de ocupare (IR/ultrasonici) '
    'transmit semnale digitale GPIO. Scannerul QR GM65 comunică prin USB HID sau serial. '
    'Senzorul BMP280 utilizează I2C. ESP32-CAM furnizează fluxul video prin RTSP sau '
    'HTTP MJPEG.'
)

h('5.3. Interfața software', level=2)
para(
    'Google Maps API este utilizat prin SDK-ul Flutter pentru hărți și rute GPS (HTTPS). '
    'Un server SMTP extern (Nodemailer) asigură trimiterea emailurilor prin SMTP/TLS. '
    'PostgreSQL 16 este accesat exclusiv prin Prisma ORM. Mosquitto MQTT 2.0 este '
    'accesibil pe portul 1883 (TCP) și 9001 (WebSocket). Docker orchestrează toate '
    'serviciile containerizate.'
)

h('5.4. Interfața de comunicare', level=2)
para(
    'API-ul backend este accesibil pe portul 3000 (HTTP/REST). Brokerul MQTT pe portul '
    '1883 (TCP) și 9001 (WebSocket). PostgreSQL pe portul 5432 (intern Docker). Adminer '
    'pe portul 8080 și dashboard-ul web static pe portul 8091. Adresa IP locală a '
    'serverului este detectată și configurată automat de scriptul start.py la fiecare '
    'pornire a sistemului.'
)
doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════
# 6. ALTE CERINȚE
# ═══════════════════════════════════════════════════════════════════════════
h('6. Alte cerințe', level=1)

h('6.1. Cerințe de instalare și configurare', level=2)
para(
    'Sistemul suportă pornirea completă printr-un singur script (start.py), care detectează '
    'automat adresa IP locală și actualizează configurația aplicației mobile. Baza de date '
    'se inițializează automat cu date de test la prima pornire (seed Prisma), incluzând '
    'utilizatorul admin, utilizatorul standard și cele 20 de locuri de parcare.'
)

h('6.2. Cerințe de documentare', level=2)
para(
    'Toate endpoint-urile API sunt documentate cu parametrii de intrare, formatul '
    'răspunsului și codurile de eroare. Schema bazei de date este versionată prin '
    'migrări Prisma cu descrieri clare. Fișierele de configurare principale '
    '(config.json, docker-compose.yml) conțin comentarii explicative.'
)

h('6.3. Cerințe de scalabilitate', level=2)
para(
    'Numărul de locuri de parcare poate fi extins prin adăugare de înregistrări în baza '
    'de date și configurare hardware, fără modificări ale codului server. Serviciile '
    'Docker permit scalarea orizontală independentă. Schema bazei de date suportă '
    'adăugarea de noi tipuri de preferințe sau entități în versiunile viitoare.'
)

# Forțează Word să evalueze câmpurile (PAGE) la deschidere
from docx.oxml import OxmlElement as _OE2
settings = doc.settings.element
upd = _OE2('w:updateFields')
upd.set(qn('w:val'), 'true')
settings.append(upd)

out = '/Users/davidandrei/Projects/smart-parking/docs/SRS_Smart_Parking.docx'
doc.save(out)
print(f'SRS generat: {out}')
