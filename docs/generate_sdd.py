"""
Generator SDD – format academic standard românesc (lucrare de licență)
Times New Roman 12pt, rânduri la 1.5, justify, margini standard, fără tabele.
"""
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

FONT = 'Times New Roman'
SB   = Pt(12)
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
sn.font.name = FONT; sn.font.size = SB
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
hp0 = sec.header.paragraphs[0]
hp0.text = ''
hp0.paragraph_format.space_after  = Pt(0)
hp0.paragraph_format.space_before = Pt(0)

htbl = sec.header.add_table(rows=1, cols=2, width=Cm(16))
htbl.style = 'Table Grid'
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

cl = htbl.cell(0, 0)
cl.width = Cm(10)
pl = cl.paragraphs[0]
pl.alignment = WD_ALIGN_PARAGRAPH.LEFT
pl.paragraph_format.space_after  = Pt(0)
pl.paragraph_format.space_before = Pt(0)
rl = pl.add_run('Universitatea Tehnică de Construcții București')
rl.font.name = FONT; rl.font.size = Pt(9); rl.italic = True

cr = htbl.cell(0, 1)
cr.width = Cm(6)
pr = cr.paragraphs[0]
pr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
pr.paragraph_format.space_after  = Pt(0)
pr.paragraph_format.space_before = Pt(0)
rr = pr.add_run('SDD – Sistem de Parcare Inteligentă')
rr.font.name = FONT; rr.font.size = Pt(9); rr.italic = True

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
cp('DOCUMENT DE SPECIFICARE A PROIECTĂRII SOFTWARE', 16, bold=True, sb=24, sa=12)
cp('(Software Design Document – SDD)', 13, sa=12)
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
    ('1.2. Domeniul de aplicare', True),
    ('1.3. Definiții și abrevieri', True),
    ('1.4. Referințe', True),
    ('2. Prezentare generală a proiectării', False),
    ('2.1. Context și constrângeri', True),
    ('2.2. Obiective de proiectare', True),
    ('2.3. Principii arhitecturale', True),
    ('3. Arhitectura sistemului', False),
    ('3.1. Prezentare arhitecturală generală', True),
    ('3.2. Subsistemul hardware IoT', True),
    ('3.3. Subsistemul backend NestJS', True),
    ('3.4. Subsistemul mobil Flutter', True),
    ('3.5. Subsistemul de detecție video', True),
    ('3.6. Infrastructura Docker', True),
    ('3.7. Fluxuri de date principale', True),
    ('4. Proiectarea datelor și a interfețelor cu utilizatorul', False),
    ('4.1. Modelul de date', True),
    ('4.2. Diagrama entitate-relație', True),
    ('4.3. Proiectarea interfețelor mobile', True),
    ('4.4. Proiectarea API REST', True),
    ('4.5. Proiectarea canalelor MQTT', True),
    ('5. Scenariile de utilizare', False),
    ('5.1. Scenariu: Înregistrare și verificare email', True),
    ('5.2. Scenariu: Autentificare și generare QR', True),
    ('5.3. Scenariu: Check-in prin scanare QR', True),
    ('5.4. Scenariu: Navigare GPS la locul alocat', True),
    ('5.5. Scenariu: Check-out și calculul costului', True),
    ('5.6. Scenariu: Monitorizare administrator', True),
    ('5.7. Scenariu: Detecție video și actualizare stare', True),
    ('6. Proiectarea de detaliu', False),
    ('6.1. Modulul de autentificare și autorizare', True),
    ('6.2. Modulul MQTT și integrare IoT', True),
    ('6.3. Modulul de gestionare a locurilor', True),
    ('6.4. Modulul de sesiuni', True),
    ('6.5. Modulul de detecție video', True),
    ('6.6. Modulul mobil Flutter', True),
    ('6.7. Tratarea erorilor și cazuri excepționale', True),
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
    'Prezentul document constituie Specificarea Proiectării Software (Software Design '
    'Document – SDD) pentru sistemul de parcare inteligentă Smart Parking. Documentul '
    'descrie arhitectura sistemului, modelul de date, proiectarea interfețelor, '
    'scenariile de utilizare și detaliile de implementare ale componentelor principale, '
    'servind ca ghid tehnic pentru dezvoltarea și mentenanța ulterioară a sistemului.'
)

h('1.2. Domeniul de aplicare', level=2)
para(
    'Documentul acoperă toate componentele sistemului Smart Parking: subsistemul hardware '
    'IoT (ESP32, senzori, servomotoare, scanner QR GM65, ESP32-CAM), subsistemul backend '
    '(NestJS, PostgreSQL, Prisma, Mosquitto MQTT), subsistemul mobil (Flutter) și '
    'subsistemul de detecție video (Python, OpenCV). Nu sunt acoperite aspectele de '
    'instalare fizică a hardware-ului sau configurarea infrastructurii de rețea.'
)

h('1.3. Definiții și abrevieri', level=2)
para('Abrevierile utilizate în prezentul document sunt identice celor din documentul SRS. '
     'Termenii suplimentari specifici proiectării sunt:')
lbl('SDD', 'Software Design Document – Document de Specificare a Proiectării Software')
lbl('DTO', 'Data Transfer Object – obiect utilizat pentru transferul datelor între straturi')
lbl('Guard', 'mecanism NestJS de verificare a autorizării înainte de procesarea unui request')
lbl('Decorator', 'adnotare TypeScript/NestJS aplicată claselor și metodelor pentru comportament declarativ')
lbl('PWM', 'Pulse Width Modulation – modulare în lățime de puls, utilizată pentru controlul servomotorului')
lbl('MOG2', 'Mixture of Gaussians v2 – algoritm de subtracție de fundal din biblioteca OpenCV')
lbl('HID', 'Human Interface Device – clasă USB pentru dispozitive de intrare, inclusiv scannerul GM65')
lbl('RTSP', 'Real Time Streaming Protocol – protocol pentru transmisia fluxurilor video')
lbl('MJPEG', 'Motion JPEG – format de streaming video prin HTTP, utilizat de ESP32-CAM')

h('1.4. Referințe', level=2)
para(
    'Prezentul document se bazează pe: [1] SRS_Smart_Parking.docx – Documentul de '
    'Specificare a Cerințelor Software, versiunea 1.0; [2] NestJS Documentation, '
    'https://docs.nestjs.com; [3] Prisma Documentation, https://www.prisma.io/docs; '
    '[4] Flutter Documentation, https://docs.flutter.dev; [5] OpenCV Documentation, '
    'https://docs.opencv.org; [6] Eclipse Mosquitto Documentation, https://mosquitto.org; '
    '[7] ESP32 Technical Reference Manual, Espressif Systems.'
)
doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════
# 2. PREZENTARE GENERALĂ A PROIECTĂRII
# ═══════════════════════════════════════════════════════════════════════════
h('2. Prezentare generală a proiectării', level=1)

h('2.1. Context și constrângeri', level=2)
para(
    'Sistemul Smart Parking este proiectat pentru o parcare cu 20 de locuri, în configurație '
    'completă: senzori fizici, bariere servo, cameră de supraveghere și aplicație mobilă. '
    'Constrângerile de proiectare includ comunicarea în timp real (latență sub 1 secundă), '
    'compatibilitatea mobilă cross-platform (iOS și Android), securitatea datelor utilizatorilor '
    'și posibilitatea de extindere viitoare a numărului de locuri fără refactorizare majoră.'
)
para(
    'Sistemul trebuie să funcționeze complet pe o rețea locală, cu o singură dependență '
    'externă (Google Maps API). Toate serviciile sunt containerizate Docker pentru portabilitate '
    'și reproducibilitate. Microcontrolerele ESP32 impun utilizarea protocolului MQTT, '
    'lightweight și eficient pentru comunicarea IoT.'
)

h('2.2. Obiective de proiectare', level=2)
para(
    'Proiectarea sistemului urmărește atingerea următoarelor obiective principale: '
    'separarea clară a responsabilităților prin arhitectura în straturi (hardware, server, '
    'mobil); comunicarea asincronă și non-blocantă prin MQTT și polling periodic; '
    'securitatea prin design prin JWT, bcrypt, Flutter Secure Storage și validare strictă '
    'a datelor de intrare; integritatea datelor garantată prin tranzacții atomice la '
    'alocarea locurilor; extensibilitatea – noi locuri, preferințe sau funcționalități pot '
    'fi adăugate fără modificări majore ale codului existent; simplitatea operațională '
    'prin pornire cu un singur script și configurare automată a adresei IP.'
)

h('2.3. Principii arhitecturale', level=2)
para(
    'Proiectarea respectă principiile arhitecturale consacrate. Principiul responsabilității '
    'unice (SRP) este aplicat la nivelul modulelor NestJS: fiecare modul gestionează o '
    'singură preocupare (autentificare, parcare, MQTT, email). Principiul deschis-închis '
    '(OCP) se reflectă în posibilitatea adăugării de noi senzori sau tipuri de preferințe '
    'fără a modifica codul existent.'
)
para(
    'Injecția de dependențe (DI), nativă în NestJS, facilitează testarea și înlocuirea '
    'componentelor. Arhitectura publish-subscribe prin MQTT decuplează producătorii de '
    'evenimente (ESP32, Python) de consumatori (NestJS), permițând evoluția independentă '
    'a componentelor. Containerizarea Docker asigură portabilitatea și izolarea serviciilor.'
)
doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════
# 3. ARHITECTURA SISTEMULUI
# ═══════════════════════════════════════════════════════════════════════════
h('3. Arhitectura sistemului', level=1)

h('3.1. Prezentare arhitecturală generală', level=2)
para(
    'Sistemul Smart Parking adoptă o arhitectură pe patru niveluri: nivelul hardware IoT, '
    'nivelul de comunicare (MQTT), nivelul backend și nivelul interfață (mobil). Fiecare '
    'nivel comunică exclusiv cu nivelul adiacent, asigurând separarea preocupărilor și '
    'independența componentelor.'
)
para(
    'La nivelul hardware se află microcontrolerele ESP32 care gestionează senzorii fizici, '
    'servomotoarele barierelor și camera de supraveghere. Aceste dispozitive comunică '
    'bidirecțional cu serverul prin brokerul MQTT Mosquitto, publicând stări și recepționând '
    'comenzi. Serverul NestJS procesează evenimentele, persistă datele în PostgreSQL prin '
    'Prisma și expune un API REST consumat de aplicația mobilă Flutter.'
)

h('3.2. Subsistemul hardware IoT', level=2)
para(
    'Subsistemul hardware este compus din trei tipuri de componente ESP32. Prima componentă '
    'este ESP32-ul de acces, care gestionează senzorii de prezență (IR sau ultrasonici) și '
    'servomotoarele barierelor. La detectarea unui vehicul, publică pe topic-ul '
    'parking/sensor/{spotName} mesajul "OCCUPIED" sau "FREE". La primirea comenzii '
    'OPEN_ENTRY sau OPEN_EXIT pe parking/commands, activează servomotorul corespunzător '
    'timp de 2 secunde, deschizând bariera.'
)
para(
    'A doua componentă este ESP32-ul cu senzori de mediu (BMP280 prin I2C), care publică '
    'periodic temperatura, umiditatea, presiunea și starea detectorului de flacără pe '
    'topic-ul parking/environment. A treia componentă este ESP32-CAM, care furnizează '
    'un flux video continuu prin HTTP MJPEG sau RTSP, vizibil în aplicația de administrare '
    'și procesabil de modulul OpenCV.'
)
para(
    'Scannerul QR GM65 este conectat la ESP32 prin serial (RS-232) sau direct la server '
    'prin USB HID. Codul QR citit este transmis pe topic-ul MQTT parking/scan sau direct '
    'la endpoint-ul REST /parking/hardware-scan, în funcție de configurația hardware.'
)

h('3.3. Subsistemul backend NestJS', level=2)
para(
    'Backend-ul este structurat conform arhitecturii modulare NestJS, compus din șapte '
    'module principale. Modulul AuthModule gestionează înregistrarea, autentificarea JWT, '
    'verificarea emailului și resetarea parolei. Modulul ParkingModule implementează '
    'logica de business pentru check-in, check-out, alocare locuri și gestionarea '
    'sesiunilor. Modulul SpotsModule expune CRUD-ul pentru locurile de parcare.'
)
para(
    'Modulul MqttModule asigură conexiunea la brokerul Mosquitto prin biblioteca asyncmqtt '
    'și procesarea asincronă a tuturor mesajelor primite pe topic-urile subscrise. '
    'Modulul EmailModule utilizează Nodemailer pentru trimiterea emailurilor transacționale '
    '(verificare cont, resetare parolă). Modulul PrismaModule expune clientul Prisma '
    'global, utilizat prin injecție de dependențe în toate modulele care accesează baza '
    'de date. Modulul HealthModule expune endpoint-ul /health pentru monitorizarea externă.'
)
para(
    'Stratul de acces la date este gestionat exclusiv prin Prisma ORM, care abstractizează '
    'complet interacțiunile cu PostgreSQL. Migrările de schemă sunt versionare și rulate '
    'automat la deployment. Tranzacțiile atomice sunt utilizate pentru operațiunile '
    'critice, precum alocarea unui loc de parcare.'
)

h('3.4. Subsistemul mobil Flutter', level=2)
para(
    'Aplicația Flutter este structurată pe straturi: stratul de prezentare (Screens și '
    'Widgets), stratul de servicii (ApiService, AuthService, MqttService) și stratul '
    'de date (modele Dart). Comunicarea cu backend-ul se realizează prin HTTP (pachetul '
    'http al Flutter), cu token JWT inclus în header-ul Authorization al fiecărei cereri.'
)
para(
    'Navigarea aplicației este implementată cu Navigator 2.0 și un sistem de rute named. '
    'Aplicația utilizează un TabBar pentru separarea ecranelor principale, cu tab-uri '
    'diferite pentru utilizatorul standard și pentru administrator. Autentificarea '
    'biometrică este gestionată prin pachetul local_auth, cu stocare securizată a '
    'credențialelor prin flutter_secure_storage.'
)
para(
    'Harta interactivă este implementată cu google_maps_flutter. Locurile de parcare sunt '
    'reprezentate ca markere sau poligoane color-codificate, actualizate la fiecare polling '
    'de 3 secunde. Navigarea GPS afișează o polilinie calculată între locația GPS curentă '
    '(geolocator) și coordonatele locului alocat.'
)

h('3.5. Subsistemul de detecție video', level=2)
para(
    'Modulul de viziune artificială este implementat în Python 3 utilizând biblioteca '
    'OpenCV (cv2). Scriptul detect_spots.py citește continuu frame-uri din sursa video '
    'configurată (cameră USB, stream RTSP sau fișier video). Pentru fiecare frame, aplică '
    'algoritmul BackgroundSubtractorMOG2 care separă prim-planul (vehiculele) de fundal '
    '(suprafața parcării).'
)
para(
    'Pentru fiecare loc de parcare, modulul analizează regiunea de interes (ROI) definită '
    'prin calibrare. Dacă mai mult de 15% din pixelii ROI aparțin prim-planului, locul '
    'este considerat ocupat. Un mecanism de debouncing cu o fereastră de 3 frame-uri '
    'consecutive previne tranzițiile false cauzate de umbre sau artefacte video. '
    'Rezultatele sunt publicate pe topic-urile MQTT parking/sensor/{spotName}.'
)

h('3.6. Infrastructura Docker', level=2)
para(
    'Serviciile server-side sunt orchestrate prin Docker Compose într-un fișier '
    'docker-compose.yml. Serviciul db rulează PostgreSQL 16 pe portul 5432, cu volum '
    'persistent pentru date. Serviciul adminer expune interfața web Adminer pe portul '
    '8080. Serviciul mqtt rulează Mosquitto 2.0 pe porturile 1883 (TCP) și 9001 '
    '(WebSocket), cu configurația din fișierul mosquitto.conf.'
)
para(
    'Serviciul dashboard rulează un server HTTP static pe portul 8091, servind '
    'fișierul dashboard.html. Serviciul api rulează containerul NestJS construit '
    'din Dockerfile, pe portul 3000. Toate serviciile sunt configurate cu politica '
    'restart: unless-stopped și comunică printr-o rețea Docker internă dedicată.'
)

h('3.7. Fluxuri de date principale', level=2)
para(
    'Fluxul de date la check-in urmează traseul: utilizatorul prezintă codul QR la '
    'scannerul fizic GM65 → scannerul publică pe MQTT parking/scan sau POST '
    '/parking/hardware-scan → MqttModule sau ParkingController recepționează → '
    'ParkingService alocă locul optim prin tranzacție Prisma → actualizează Spot '
    '(status=RESERVED), creează Session → publică OPEN_ENTRY pe parking/commands → '
    'ESP32 deschide bariera → publishează starea completă pe parking/status.'
)
para(
    'Fluxul de actualizare a stării prin senzori urmează: senzorul ESP32 detectează '
    'vehicul → publică OCCUPIED pe parking/sensor/A1 → MqttModule recepționează → '
    'ParkingService actualizează Spot(status=OCCUPIED) în baza de date → publică '
    'starea actualizată pe parking/status → aplicația mobilă recepționează la '
    'polling-ul de 3 secunde și actualizează harta.'
)
doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════
# 4. PROIECTAREA DATELOR ȘI INTERFEȚELOR CU UTILIZATORUL
# ═══════════════════════════════════════════════════════════════════════════
h('4. Proiectarea datelor și a interfețelor cu utilizatorul', level=1)

h('4.1. Modelul de date', level=2)
para(
    'Schema bazei de date PostgreSQL este definită și gestionată prin Prisma ORM, cu '
    'versionarea controlată prin migrări. Modelul cuprinde patru entități principale: '
    'User, Spot, Session și ParkingConfig.'
)
para(
    'Entitatea User stochează datele utilizatorilor: identificator UUID unic, adresă '
    'de email unică, hash bcrypt al parolei, rolul utilizatorului (USER sau ADMIN), '
    'codul QR unic hexazecimal, culoarea mașinii, preferința de parcare, câmpurile '
    'de verificare a emailului (token, flag boolean) și câmpurile de resetare a '
    'parolei (token, timestamp expirare). Câmpul preferredSpotId referențiază opțional '
    'un loc specific din entitatea Spot.'
)
para(
    'Entitatea Spot reprezintă un loc de parcare și conține: identificator UUID, '
    'denumire unică (ex: A1, B5), starea curentă (AVAILABLE, OCCUPIED sau RESERVED), '
    'coordonatele GPS (latitudine și longitudine ca Double), lista sesiunilor '
    'asociate și lista utilizatorilor care au setat acel loc ca preferință.'
)
para(
    'Entitatea Session reprezintă o utilizare a parcării: identificator UUID, '
    'referință la utilizator (userId) și la loc (spotId), timestamp de start '
    '(startTime), timestamp opțional de final (endTime) și costul calculat (cost). '
    'Sesiunile active au endTime null.'
)
para(
    'Entitatea ParkingConfig stochează configurația globală a parcării: identificator '
    'UUID, coordonatele GPS ale intrării, ieșirii și zonei de magazine (câte două '
    'câmpuri Double pentru latitudine și longitudine), tariful orar și limita de '
    'viteză. Sistemul menține o singură înregistrare de configurație.'
)

h('4.2. Diagrama entitate-relație', level=2)
para(
    'Relațiile dintre entitățile principale sunt descrise textual în absența unui '
    'instrument de generare de diagrame. Un utilizator (User) poate avea zero sau mai '
    'multe sesiuni de parcare (Session), relație de tipul unu-la-multe. Un loc de '
    'parcare (Spot) poate apărea în zero sau mai multe sesiuni (Session), relație '
    'unu-la-multe. Un utilizator poate selecta un loc preferat (Spot), relație opțională '
    'unu-la-unu implementată prin câmpul preferredSpotId din User.'
)
para(
    'ParkingConfig este o entitate independentă fără relații externe, accesată global '
    'de toate modulele care necesită parametrii de configurare ai parcării. Toate '
    'cheile primare utilizează tipul UUID (String cu @default(uuid())), iar toate '
    'relațiile utilizează ștergere în cascadă la nivel de aplicație, nu la nivelul '
    'bazei de date, pentru control granular.'
)

h('4.3. Proiectarea interfețelor mobile', level=2)
para(
    'Aplicația mobilă este organizată în două fluxuri de navigare distincte, în funcție '
    'de rolul utilizatorului autentificat. Fluxul de autentificare include: ecranul de '
    'login (câmpuri email/parolă, buton biometric dacă este disponibil, link către '
    'înregistrare și recuperare parolă), ecranul de înregistrare (câmpuri email, '
    'parolă, confirmare parolă, culoare mașină), ecranul de verificare email '
    '(notificare de confirmare), ecranul de recuperare parolă și ecranul de '
    'resetare parolă.'
)
para(
    'Interfața utilizatorului standard constă dintr-un TabBar cu patru file. Prima '
    'filă afișează codul QR al utilizatorului centrat pe ecran, pregătit pentru '
    'scanare. A doua filă prezintă harta interactivă a parcării cu 20 de locuri '
    'color-codificate și butonul de navigare GPS. A treia filă afișează istoricul '
    'sesiunilor în ordine cronologică inversă, cu locul, data, durata și costul. '
    'A patra filă conține preferința de parcare, culoarea mașinii și butonul de logout.'
)
para(
    'Interfața administratorului extinde cea a utilizatorului standard cu file '
    'suplimentare: dashboard în timp real cu statistici (locuri disponibile/ocupate, '
    'sesiuni active), editor de parcare pentru configurarea coordonatelor și tarifului, '
    'scanner QR prin camera telefonului, vizualizator flux video live și vizualizator '
    'informații sistem (versiune, IP server, stare conexiuni).'
)

h('4.4. Proiectarea API REST', level=2)
para(
    'API-ul REST NestJS este organizat pe prefixe de rută corespunzătoare modulelor. '
    'Modulul de autentificare expune endpoint-urile: POST /auth/register (înregistrare '
    'utilizator), POST /auth/login (autentificare cu JWT), GET /auth/verify-email '
    '(confirmare adresă email), POST /auth/forgot-password (solicitare resetare), '
    'POST /auth/reset-password (schimbare parolă cu token), GET /auth/profile '
    '(profil utilizator autentificat), PATCH /auth/profile (actualizare profil).'
)
para(
    'Modulul de parcare expune: POST /parking/checkin (check-in prin QR, necesită '
    'autentificare), POST /parking/checkout (check-out, necesită autentificare), '
    'POST /parking/hardware-scan (check-in/out din hardware fără JWT, securizat prin '
    'rețeaua internă), GET /parking/active-session (sesiunea activă curentă), '
    'GET /parking/history (istoricul sesiunilor utilizatorului), GET /parking/config '
    '(configurația parcării), PATCH /parking/config (actualizare configurație, doar admin), '
    'GET /parking/mqtt-log (jurnalul MQTT, doar admin).'
)
para(
    'Modulul de locuri expune: GET /spots (lista tuturor locurilor cu stări), '
    'POST /spots (creare loc, admin), PATCH /spots/:id (actualizare stare sau '
    'coordonate, admin), DELETE /spots/:id (ștergere loc, admin). Toate endpoint-urile '
    'protejate utilizează JwtAuthGuard, iar cele de admin utilizează suplimentar '
    'RolesGuard cu decoratorul @Roles("admin").'
)

h('4.5. Proiectarea canalelor MQTT', level=2)
para(
    'Comunicarea MQTT este structurată pe șase topic-uri principale, fiecare cu o '
    'responsabilitate definită. Topic-ul parking/sensor/{spotName} transportă mesajele '
    '"OCCUPIED" sau "FREE" de la senzori sau modulul Python, unde {spotName} este '
    'denumirea locului (A1, B3 etc.). Topic-ul parking/scan primește codul QR scanat, '
    'declanșând procesarea check-in/out.'
)
para(
    'Topic-ul parking/commands este utilizat de server pentru a publica comenzile '
    'OPEN_ENTRY și OPEN_EXIT receptate de ESP32 pentru controlul barierelor. '
    'Topic-ul parking/status este publicat de server după fiecare schimbare de stare, '
    'conținând JSON cu lista completă a locurilor și stările lor curente. Topic-ul '
    'parking/environment primește datele de mediu de la senzori (temperatură, umiditate, '
    'presiune, flacără), iar topic-ul parking/speed primește date de la senzorul de viteză.'
)
doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════
# 5. SCENARIILE DE UTILIZARE
# ═══════════════════════════════════════════════════════════════════════════
h('5. Scenariile de utilizare', level=1)

h('5.1. Scenariu: Înregistrare și verificare email', level=2)
para(
    'Actori implicați: utilizator nou, server NestJS, server SMTP. Precondițiile '
    'scenariului: utilizatorul nu are cont în sistem.'
)
para(
    'Utilizatorul completează formularul de înregistrare cu adresa de email, parola și '
    'culoarea mașinii, apoi apasă butonul de înregistrare. Aplicația mobilă trimite '
    'o cerere POST /auth/register. Serverul validează câmpurile (email unic, parolă '
    'minimă 6 caractere), calculează hash-ul bcrypt al parolei și creează înregistrarea '
    'User în baza de date cu câmpul isEmailVerified=false. Generează un token de '
    'verificare aleator (hex 32 octeți) și trimite email-ul de verificare prin Nodemailer.'
)
para(
    'Utilizatorul accesează link-ul din email. Serverul validează token-ul, marchează '
    'contul cu isEmailVerified=true și curăță token-ul de verificare. Utilizatorul este '
    'redirecționat la ecranul de login cu un mesaj de confirmare. Postcondițiile: '
    'contul este activ, utilizatorul poate autentifica.'
)

h('5.2. Scenariu: Autentificare și generare QR', level=2)
para(
    'Actori implicați: utilizator înregistrat, server NestJS. Precondițiile: contul '
    'este activ (email verificat).'
)
para(
    'Utilizatorul introduce email-ul și parola în ecranul de login și apasă "Autentifică-te". '
    'Aplicația trimite POST /auth/login. Serverul verifică existența utilizatorului, '
    'compară parola furnizată cu hash-ul bcrypt stocat. La potrivire, verifică dacă '
    'utilizatorul are deja un cod QR generat (câmpul qrCode). Dacă nu, generează un '
    'nou cod hexazecimal de 16 octeți, garantat unic, și îl persistă.'
)
para(
    'Serverul semnează un token JWT cu payload-ul {sub: userId, email, role} și '
    'îl returnează împreună cu datele profilului. Aplicația stochează token-ul în '
    'Flutter Secure Storage și navighează la ecranul principal. Prima filă afișează '
    'codul QR generat. Postcondițiile: utilizatorul este autentificat, JWT stocat, '
    'codul QR vizibil.'
)

h('5.3. Scenariu: Check-in prin scanare QR', level=2)
para(
    'Actori implicați: utilizator, scanner GM65, server NestJS, ESP32 barieră intrare. '
    'Precondițiile: utilizatorul nu are sesiune activă, există cel puțin un loc disponibil.'
)
para(
    'Utilizatorul prezintă codul QR la scannerul GM65 de la bariera de intrare. Scannerul '
    'citește codul și îl publică pe topic-ul MQTT parking/scan. MqttModule din NestJS '
    'recepționează mesajul și apelează ParkingService.processQrScan(). Serviciul '
    'determină că utilizatorul nu are sesiune activă (check-in) și calculează locul '
    'optim conform preferinței configurate: dacă preferința este un loc specific '
    '(spotPreference = spot_id), încearcă acel loc; altfel aplică logica de distanță '
    'minimă față de intrare, ieșire sau magazine.'
)
para(
    'Alocarea se realizează printr-o tranzacție Prisma care actualizează starea locului '
    'la RESERVED și creează sesiunea nouă atomic. Serviciul publică comanda OPEN_ENTRY '
    'pe topic-ul parking/commands, iar ESP32 activează servomotorul barierei de intrare '
    'timp de 2 secunde. Starea completă a locurilor este publicată pe parking/status. '
    'Postcondițiile: locul este rezervat, sesiunea activă creată, bariera deschisă.'
)

h('5.4. Scenariu: Navigare GPS la locul alocat', level=2)
para(
    'Actori implicați: utilizator autentificat cu sesiune activă, API Google Maps. '
    'Precondițiile: utilizatorul are o sesiune activă cu loc alocat.'
)
para(
    'Utilizatorul accesează fila cu harta parcării. Aplicația interoghează GET '
    '/parking/active-session și primește locul alocat cu coordonatele GPS. Utilizatorul '
    'apasă butonul "Navighează". Aplicația solicită permisiunea de localizare (dacă nu '
    'a fost deja acordată), obține poziția GPS curentă prin pachetul geolocator și '
    'inițializează Google Maps cu o polilinie de la coordonatele curente la coordonatele '
    'locului alocat.'
)
para(
    'Harta se actualizează continuu pe măsura deplasării utilizatorului, recalculând '
    'distanța rămasă și afișând direcția. La apropierea de destinație (sub 10 metri), '
    'aplicația afișează un mesaj de confirmare că utilizatorul a ajuns la locul alocat. '
    'Postcondițiile: utilizatorul a navigat cu succes la locul rezervat.'
)

h('5.5. Scenariu: Check-out și calculul costului', level=2)
para(
    'Actori implicați: utilizator cu sesiune activă, scanner GM65, server NestJS, '
    'ESP32 barieră ieșire. Precondițiile: utilizatorul are o sesiune activă.'
)
para(
    'Utilizatorul prezintă codul QR la scannerul de la bariera de ieșire. Scannerul '
    'publică pe parking/scan. MqttModule recepționează și apelează ParkingService. '
    'Serviciul detectează că utilizatorul are o sesiune activă (endTime este null) '
    'și procesează check-out-ul: actualizează endTime = momentul curent, calculează '
    'durata în ore (endTime - startTime), calculează costul = durată × tarif orar '
    'din ParkingConfig.'
)
para(
    'Serviciul actualizează Session cu endTime și cost, schimbă starea Spot la '
    'AVAILABLE și publică OPEN_EXIT pe parking/commands pentru deschiderea barierei '
    'de ieșire. Publică starea completă actualizată pe parking/status. '
    'Postcondițiile: sesiunea finalizată, costul calculat, locul disponibil, '
    'bariera deschisă.'
)

h('5.6. Scenariu: Monitorizare administrator', level=2)
para(
    'Actori implicați: administrator, server NestJS. Precondițiile: utilizatorul '
    'are rolul ADMIN.'
)
para(
    'Administratorul autentificat accesează fila Dashboard. Aplicația interoghează '
    'GET /spots pentru starea tuturor locurilor și GET /parking/history pentru '
    'sesiunile active și recente. Dashboard-ul afișează numărul de locuri disponibile, '
    'ocupate și rezervate, lista sesiunilor active cu utilizatorul și locul aferent, '
    'și butoanele de control al barierelor.'
)
para(
    'La apăsarea unui buton BYPASS de deschidere a barierei, aplicația trimite o '
    'cerere autentificată (JWT cu rol admin) care publică direct comanda MQTT corespunzătoare. '
    'Administratorul poate accesa ecranul de configurare pentru a modifica tarifele '
    'sau coordonatele GPS, prin PATCH /parking/config cu verificarea rolului admin pe server. '
    'Postcondițiile: administratorul are vizibilitate completă și control operațional.'
)

h('5.7. Scenariu: Detecție video și actualizare stare', level=2)
para(
    'Actori implicați: modulul Python OpenCV, broker MQTT, server NestJS. '
    'Precondițiile: camera video este funcțională, modulul Python rulează.'
)
para(
    'Modulul Python detect_spots.py citește frame-uri continuu din sursa video. '
    'Pentru fiecare frame, aplică BackgroundSubtractorMOG2 și analizează ROI-ul '
    'fiecărui loc calibrat. Dacă procentul de pixeli activi depășește pragul de 15%, '
    'locul este marcat ca "potențial ocupat" în fereastra de debouncing.'
)
para(
    'După confirmarea stării în 3 frame-uri consecutive, modulul verifică dacă starea '
    's-a schimbat față de ultima stare publicată. Dacă da, publică "OCCUPIED" sau "FREE" '
    'pe parking/sensor/{spotName}. Serverul NestJS recepționează prin MqttModule și '
    'actualizează baza de date, publicând starea completă actualizată pe parking/status. '
    'Postcondițiile: starea locului reflectă realitatea fizică cu o latență sub 1 secundă.'
)
doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════
# 6. PROIECTAREA DE DETALIU
# ═══════════════════════════════════════════════════════════════════════════
h('6. Proiectarea de detaliu', level=1)

h('6.1. Modulul de autentificare și autorizare', level=2)
para(
    'Modulul AuthModule implementează fluxul complet de gestionare a identității. '
    'La înregistrare, AuthService primește datele prin RegisterDto (validat cu class-validator), '
    'verifică unicitatea email-ului, calculează hash-ul bcrypt cu 10 runde și persistă '
    'utilizatorul. Generarea token-ului de verificare email utilizează crypto.randomBytes(32).'
)
para(
    'Autentificarea utilizează strategia JWT din Passport.js. AuthController definește '
    'endpoint-ul POST /auth/login care returnează token-ul JWT semnat cu cheia secretă '
    'din variabilele de mediu. JwtAuthGuard este aplicat global, exceptând explicit '
    'endpoint-urile publice prin decoratorul @Public(). RolesGuard verifică câmpul '
    'role din payload-ul JWT pentru endpoint-urile de administrator.'
)
para(
    'Resetarea parolei generează un token aleator (hex 32 octeți) cu timestamp de '
    'expirare (Date.now() + 3600000 ms). La resetare, serverul verifică existența '
    'token-ului, valabilitatea temporală și invalidează token-ul după utilizare '
    'prin setarea câmpurilor de resetare la null.'
)

h('6.2. Modulul MQTT și integrare IoT', level=2)
para(
    'MqttModule utilizează biblioteca asyncmqtt pentru conexiunea la brokerul Mosquitto '
    'prin TCP. La pornirea aplicației (onApplicationBootstrap), MqttService se conectează '
    'cu opțiunile din configurație (host, port 1883, clientId unic) și se abonează la '
    'topic-urile: parking/sensor/#, parking/scan, parking/environment, parking/speed, '
    'parking/diagnostics, utilizând wildcard "#" pentru toate sub-topic-urile senzorilor.'
)
para(
    'Procesarea mesajelor este asincronă. MqttService parsează payload-ul fiecărui mesaj '
    'și apelează metoda corespunzătoare din ParkingService sau SpotsService. Logica de '
    'reconectare implementează exponential backoff cu un număr maxim de 10 tentative, '
    'după care logul de erori este actualizat. Publicarea comenzilor utilizează metoda '
    'client.publish() cu QoS nivel 1 (cel puțin o dată) pentru comenzile de barieră.'
)

h('6.3. Modulul de gestionare a locurilor', level=2)
para(
    'SpotsService implementează operațiunile CRUD pentru entitatea Spot. Metoda '
    'findOptimalSpot(userId, preference) calculează locul optim disponibil conform '
    'preferinței: dacă preferința este un loc specific, verifică dacă acel loc este '
    'disponibil; altfel, obține coordonatele de referință din ParkingConfig și calculează '
    'distanța Euclidiană de la fiecare loc disponibil, returnând cel mai apropiat.'
)
para(
    'Actualizarea stării locurilor (updateSpotStatus) este apelată atât din MqttModule '
    '(la primirea mesajelor de la senzori) cât și din ParkingService (la check-in/out). '
    'Metoda utilizează prisma.spot.update() atomic, fără necesitatea unei tranzacții '
    'separate, întrucât este o operație pe o singură înregistrare. Publicarea stării '
    'complete pe parking/status este declanșată după fiecare actualizare.'
)

h('6.4. Modulul de sesiuni', level=2)
para(
    'ParkingService implementează logica de business principală a sistemului. Metoda '
    'processCheckIn(qrCode) identifică utilizatorul prin qrCode (câmp indexat în baza '
    'de date), verifică absența unei sesiuni active, determină locul optim și execută '
    'tranzacția de alocare.'
)
para(
    'Tranzacția de check-in utilizează prisma.$transaction() cu array de operații: '
    'actualizarea stării locului la RESERVED și crearea sesiunii cu startTime = new Date(). '
    'Această abordare garantează atomicitatea: fie ambele operații reușesc, fie niciuna, '
    'prevenind stări inconsistente în caz de eroare. Metoda processCheckOut(qrCode) '
    'identifică sesiunea activă (endTime = null), calculează costul și actualizează '
    'sesiunea și locul printr-o nouă tranzacție atomică.'
)

h('6.5. Modulul de detecție video', level=2)
para(
    'Scriptul detect_spots.py este structurat în trei componente principale: inițializarea '
    '(încărcarea configurației ROI din config.json, conectarea la broker MQTT, inițializarea '
    'BackgroundSubtractorMOG2 cu parametrii history=500, varThreshold=16, detectShadows=True), '
    'bucla de procesare (citire frame, aplicare subtractor, analiză ROI, debouncing, publicare '
    'MQTT) și utilitarul de calibrare (calibrate.py cu interfață interactivă OpenCV pentru '
    'definirea ROI prin mouse drag).'
)
para(
    'Configurația ROI este stocată în config.json sub cheia "spots", ca array de obiecte '
    'cu câmpurile name (denumirea locului) și roi ([x, y, width, height] în pixeli). '
    'Starea de debouncing este menținută într-un dicționar Python {spotName: deque(maxlen=3)} '
    'unde deque stochează ultimele 3 stări detectate. O schimbare de stare este '
    'confirmată când toate cele 3 elemente din deque sunt identice și diferite de '
    'ultima stare publicată.'
)

h('6.6. Modulul mobil Flutter', level=2)
para(
    'ApiService este clasa centrală pentru comunicarea cu backend-ul, utilizând '
    'pachetul http. La fiecare cerere autentificată, adaugă header-ul '
    '"Authorization: Bearer {token}", unde token-ul este citit din Flutter Secure Storage. '
    'Gestionarea erorilor HTTP parsează răspunsurile non-2xx și extrage mesajul de eroare '
    'din câmpul "message" al body-ului JSON.'
)
para(
    'ParkingMapScreen utilizează GoogleMapController pentru manipularea hărții și '
    'un Timer.periodic de 3 secunde pentru polling-ul stărilor locurilor. Markerele '
    'sau poligoanele sunt recreate la fiecare actualizare cu culoarea corespunzătoare '
    'stării. NavigationScreen inițializează o cameră centrată pe locul alocat și '
    'desenează o Polyline cu 2 puncte: locația curentă (din geolocator) și '
    'coordonatele locului alocat.'
)
para(
    'QrScanScreen utilizează mobile_scanner pentru accesul la camera telefonului și '
    'decodificarea în timp real a codurilor QR. La detectarea unui cod valid, '
    'apelează ApiService.processQrCode(code) care trimite o cerere autentificată '
    'de check-in sau check-out în funcție de starea sesiunii active.'
)

h('6.7. Tratarea erorilor și cazuri excepționale', level=2)
para(
    'Serverul NestJS utilizează NestJS ExceptionFilter global pentru prinderea erorilor '
    'negestionate și returnarea unui răspuns JSON consistent cu câmpurile statusCode, '
    'message și timestamp. Erorile de validare (BadRequestException) sunt generate '
    'automat de ValidationPipe cu transformare activată.'
)
para(
    'Cazul în care nu există locuri disponibile la check-in este gestionat prin '
    'returnarea unui NotFoundException cu mesajul descriptiv, afișat în aplicația '
    'mobilă ca dialog de eroare. Expirarea token-ului JWT este detectată de JwtStrategy '
    'și determină redirecționarea la ecranul de login cu ștergerea credențialelor din '
    'Flutter Secure Storage.'
)
para(
    'Deconectarea MQTT în backend activează reconectarea automată cu backoff exponențial. '
    'Pierderea conexiunii Wi-Fi a ESP32 determină reconectarea automată la rețea și '
    'la brokerul MQTT, implementată în firmware-ul Arduino. Erorile de citire video '
    'în modulul Python sunt capturate, logul este actualizat și procesarea continuă '
    'cu frame-ul următor.'
)

# Forțează Word să evalueze câmpurile (PAGE) la deschidere
from docx.oxml import OxmlElement as _OE2
settings = doc.settings.element
upd = _OE2('w:updateFields')
upd.set(qn('w:val'), 'true')
settings.append(upd)

out = '/Users/davidandrei/Projects/smart-parking/docs/SDD_Smart_Parking.docx'
doc.save(out)
print(f'SDD generat: {out}')
