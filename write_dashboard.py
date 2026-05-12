import pathlib

content = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Smart Parking – Dashboard</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --bg:#1e1e2e; --surface:#313244; --surface2:#45475a; --surface3:#181825;
      --text:#cdd6f4; --sub:#a6adc8; --muted:#6c7086; --border:#45475a;
      --green:#a6e3a1; --red:#f38ba8; --blue:#89b4fa;
      --yellow:#f9e2af; --orange:#fab387; --purple:#cba6f7; --teal:#94e2d5;
    }
    html,body { height:100%; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
      background:var(--bg); color:var(--text); font-size:14px; }

    /* HEADER */
    header { display:flex; align-items:center; justify-content:space-between;
      padding:10px 20px; background:var(--surface); border-bottom:1px solid var(--border);
      position:sticky; top:0; z-index:100; gap:12px; flex-wrap:wrap; }
    header h1 { font-size:16px; font-weight:700; color:var(--blue); white-space:nowrap; }
    #clock { font-size:12px; color:var(--muted); font-family:monospace; }

    /* STATUS BAR */
    .sbar { display:flex; gap:6px; padding:8px 20px; border-bottom:1px solid var(--border);
      flex-wrap:wrap; align-items:center; }
    .pill { display:flex; align-items:center; gap:5px; padding:3px 11px; border-radius:20px;
      font-size:11px; font-weight:700; border:1px solid transparent; white-space:nowrap; }
    .pill .dot { width:7px; height:7px; border-radius:50%; flex-shrink:0; }
    .pill.ok   { background:rgba(166,227,161,.1); border-color:rgba(166,227,161,.35); color:var(--green); }
    .pill.ok   .dot { background:var(--green); box-shadow:0 0 4px var(--green); }
    .pill.err  { background:rgba(243,139,168,.1); border-color:rgba(243,139,168,.35); color:var(--red); }
    .pill.err  .dot { background:var(--red); }
    .pill.warn { background:rgba(249,226,175,.1); border-color:rgba(249,226,175,.35); color:var(--yellow); }
    .pill.warn .dot { background:var(--yellow); }
    .pill.idle { background:var(--surface); border-color:var(--border); color:var(--muted); }
    .pill.idle .dot { background:var(--muted); }
    .rbtn { margin-left:auto; cursor:pointer; background:var(--surface); border:1px solid var(--border);
      color:var(--sub); padding:3px 13px; border-radius:20px; font-size:11px; font-weight:700; }
    .rbtn:hover { background:var(--surface2); }

    /* LAYOUT */
    .main { padding:14px 20px; display:grid; gap:14px; }
    .top-row { display:grid; grid-template-columns:1fr 1fr; gap:14px; }
    @media(max-width:820px) { .top-row { grid-template-columns:1fr; } }

    /* PANEL */
    .panel { background:var(--surface); border-radius:12px; border:1px solid var(--border); overflow:hidden; }
    .ph { padding:9px 16px; border-bottom:1px solid var(--border); font-size:11px;
      font-weight:700; color:var(--sub); text-transform:uppercase; letter-spacing:.06em;
      display:flex; align-items:center; gap:8px; }
    .ph .hr { margin-left:auto; font-size:11px; color:var(--muted); text-transform:none;
      font-weight:400; letter-spacing:0; }
    .pb { padding:14px 16px; }

    /* SCANNER PANEL */
    .focus-bar { display:flex; align-items:center; gap:10px; padding:12px 16px;
      cursor:pointer; user-select:none; border-bottom:1px solid var(--border); transition:background .2s; }
    .focus-bar:hover { background:rgba(255,255,255,.02); }
    .focus-bar.active { background:rgba(166,227,161,.05); }
    .fdot { width:12px; height:12px; border-radius:50%; background:var(--muted); flex-shrink:0; transition:background .3s; }
    .fdot.on  { background:var(--green); box-shadow:0 0 7px var(--green); }
    .fdot.off { background:var(--red); }
    #scanner-input { position:absolute; left:-9999px; width:1px; height:1px; opacity:0; }
    .buf-row { padding:5px 16px; font-family:monospace; font-size:12px; color:var(--orange);
      min-height:26px; border-bottom:1px solid var(--border); }
    .last-row { padding:10px 16px; display:flex; gap:10px; align-items:flex-start; }
    .sbadge { flex-shrink:0; padding:3px 9px; border-radius:5px; font-weight:700; font-size:11px; }
    .b-ok   { background:rgba(166,227,161,.18); color:var(--green); }
    .b-err  { background:rgba(243,139,168,.18); color:var(--red);   }
    .b-idle { background:var(--surface2); color:var(--muted); }
    #last-detail { font-size:12px; color:var(--sub); word-break:break-all; }
    .manual-row { padding:8px 16px; border-top:1px solid var(--border); display:flex; gap:7px; }
    .manual-row input { flex:1; background:var(--bg); border:1px solid var(--border);
      border-radius:6px; padding:5px 9px; color:var(--text); font-size:12px; }
    .manual-row input:focus { outline:none; border-color:var(--blue); }
    .manual-row button { background:var(--blue); border:none; border-radius:6px;
      padding:5px 14px; color:#1e1e2e; font-weight:700; font-size:12px; cursor:pointer; }
    .manual-row button:hover { opacity:.85; }

    /* MOCK SCAN USERS */
    .user-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(200px,1fr)); gap:8px; }
    .user-card { background:var(--surface3); border:1px solid var(--border);
      border-radius:9px; padding:10px 12px; }
    .user-email { font-size:12px; color:var(--blue); margin-bottom:4px;
      overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
    .user-role  { font-size:10px; color:var(--muted); margin-bottom:4px; }
    .user-qr   { font-size:10px; color:var(--muted); font-family:monospace;
      margin-bottom:8px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
    .user-status { font-size:10px; font-weight:700; margin-bottom:6px; }
    .user-status.parked  { color:var(--red); }
    .user-status.free    { color:var(--green); }
    .user-actions { display:flex; gap:5px; }
    .scan-btn  { flex:1; border:none; border-radius:5px; padding:5px 0;
      font-size:11px; font-weight:700; cursor:pointer; transition:background .15s; }
    .entry-btn { background:rgba(166,227,161,.18); color:var(--green); border:1px solid rgba(166,227,161,.35); }
    .entry-btn:hover:not(:disabled) { background:rgba(166,227,161,.35); }
    .exit-btn  { background:rgba(243,139,168,.18); color:var(--red);   border:1px solid rgba(243,139,168,.35); }
    .exit-btn:hover:not(:disabled)  { background:rgba(243,139,168,.35); }
    .scan-btn:disabled { opacity:.35; cursor:not-allowed; }

    /* SPOTS */
    #spots-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(110px,1fr)); gap:10px; }
    .spot-card { border-radius:10px; padding:11px 8px; text-align:center;
      border:2px solid transparent; transition:all .3s; }
    .spot-card.available { background:rgba(166,227,161,.07); border-color:rgba(166,227,161,.25); }
    .spot-card.occupied  { background:rgba(243,139,168,.07); border-color:rgba(243,139,168,.3); }
    .spot-name  { font-size:20px; font-weight:700; margin-bottom:2px; }
    .spot-card.available .spot-name { color:var(--green); }
    .spot-card.occupied  .spot-name { color:var(--red); }
    .spot-lbl  { font-size:10px; color:var(--muted); }
    .spot-user { margin-top:3px; font-size:10px; color:var(--sub);
      overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
    /* Sensor buttons */
    .spot-btns { display:flex; gap:3px; margin-top:7px; }
    .snr-btn { flex:1; border:none; border-radius:4px; padding:4px 0;
      font-size:10px; font-weight:700; cursor:pointer; transition:background .15s; }
    .snr-occ { background:rgba(243,139,168,.18); color:var(--red);
      border:1px solid rgba(243,139,168,.35); }
    .snr-occ:hover { background:rgba(243,139,168,.38); }
    .snr-avl { background:rgba(166,227,161,.18); color:var(--green);
      border:1px solid rgba(166,227,161,.35); }
    .snr-avl:hover { background:rgba(166,227,161,.38); }

    /* SESSIONS / LOG */
    .two-col { display:grid; grid-template-columns:1fr 1fr; gap:14px; }
    @media(max-width:800px) { .two-col { grid-template-columns:1fr; } }
    .sess-table { width:100%; border-collapse:collapse; }
    .sess-table th { text-align:left; font-size:10px; text-transform:uppercase;
      letter-spacing:.05em; color:var(--muted); padding:6px 10px; border-bottom:1px solid var(--border); }
    .sess-table td { padding:8px 10px; border-bottom:1px solid rgba(69,71,90,.4); font-size:12px; }
    .sess-table tr:last-child td { border-bottom:none; }
    .ems  { max-width:140px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
    .spill { display:inline-block; padding:2px 7px; border-radius:4px;
      background:rgba(243,139,168,.15); color:var(--red); font-weight:700; font-size:11px; }
    .dur  { color:var(--yellow); font-family:monospace; font-size:11px; }
    .empty { text-align:center; color:var(--muted); padding:24px; font-size:13px; }

    /* EVENT LOG */
    #elog { height:260px; overflow-y:auto; font-family:monospace; font-size:12px; }
    .le  { padding:3px 2px; border-bottom:1px solid rgba(69,71,90,.25);
      display:flex; gap:9px; align-items:baseline; }
    .lt  { color:var(--muted); flex-shrink:0; font-size:10px; }
    .lok    { color:var(--green); }
    .lerr   { color:var(--red); }
    .linfo  { color:var(--blue); }
    .lscan  { color:var(--orange); }
    .lwarn  { color:var(--yellow); }
    .lsensor{ color:var(--teal); }

    /* DIAG */
    .diag { background:var(--surface3); border-radius:12px; border:1px solid var(--border); padding:12px 16px; }
    .diag h3 { font-size:10px; text-transform:uppercase; letter-spacing:.06em; color:var(--muted); margin-bottom:9px; }
    .dg { display:grid; grid-template-columns:repeat(auto-fill,minmax(180px,1fr)); gap:7px; }
    .di { background:var(--surface); border-radius:7px; padding:9px 12px; border-left:3px solid var(--border); }
    .di.ok   { border-left-color:var(--green); }
    .di.err  { border-left-color:var(--red); }
    .dlbl { font-size:10px; color:var(--muted); margin-bottom:2px; }
    .dval { font-size:13px; font-weight:600; }

    .sm-btn { background:var(--surface2); border:none; border-radius:4px;
      color:var(--muted); padding:2px 8px; cursor:pointer; font-size:10px; }
    .sm-btn:hover { color:var(--text); }
    ::-webkit-scrollbar { width:3px; }
    ::-webkit-scrollbar-thumb { background:var(--surface2); border-radius:2px; }
  </style>
</head>
<body>

<header>
  <h1>🚗 Smart Parking — Operations Dashboard</h1>
  <div id="clock">00:00:00</div>
</header>

<div class="sbar">
  <div class="pill idle" id="pill-api">  <span class="dot"></span> API</div>
  <div class="pill idle" id="pill-mqtt"><span class="dot"></span> MQTT</div>
  <div class="pill idle" id="pill-spots"><span class="dot"></span> Spots</div>
  <div class="pill idle" id="pill-sess"><span class="dot"></span> Sessions</div>
  <div class="pill idle" id="pill-users"><span class="dot"></span> Users</div>
  <button class="rbtn" onclick="doRefresh()">↻ Refresh</button>
</div>

<div class="main">

  <!-- ROW 1: Hardware scanner + Mock scan -->
  <div class="top-row">

    <!-- Hardware QR Scanner -->
    <div class="panel">
      <div class="ph">📷 GM65 QR Scanner
        <span class="hr">Click green bar, then scan</span>
      </div>
      <div class="focus-bar" id="focus-bar" onclick="activateScanner()">
        <div class="fdot off" id="fdot"></div>
        <span id="flabel">🔴 INACTIVE — click here to activate</span>
      </div>
      <input type="text" id="scanner-input" autocomplete="off" spellcheck="false">
      <div class="buf-row" id="buf">—</div>
      <div class="last-row">
        <div class="sbadge b-idle" id="lbadge">—</div>
        <div id="last-detail">No scans yet. Activate above, then point GM65 at a QR code.</div>
      </div>
      <div class="manual-row">
        <input type="text" id="manual-input" placeholder="Paste QR code, press Enter or Send">
        <button onclick="manualSend()">Send</button>
      </div>
    </div>

    <!-- Mock QR Scan: users list -->
    <div class="panel">
      <div class="ph">👤 Mock QR Scan — Users
        <span class="hr">Simulates a real scan for that user</span>
      </div>
      <div class="pb">
        <div class="user-grid" id="user-grid">
          <p style="color:var(--muted);font-size:12px">Loading…</p>
        </div>
      </div>
    </div>

  </div><!-- /top-row -->

  <!-- ROW 2: Spots + sensor controls -->
  <div class="panel">
    <div class="ph">🅿️ Parking Spots &amp; Sensor Simulation
      <span class="hr">🚗 In / ✓ Out simulate a physical IR/ultrasonic sensor trigger → updates DB via MQTT</span>
    </div>
    <div class="pb">
      <div id="spots-grid"><p style="color:var(--muted)">Loading spots…</p></div>
    </div>
  </div>

  <!-- ROW 3: Active sessions + Event log -->
  <div class="two-col">
    <div class="panel">
      <div class="ph">🚗 Active Sessions</div>
      <div id="sess-wrap"><p class="empty">No active sessions</p></div>
    </div>
    <div class="panel">
      <div class="ph">📋 Event Log
        <span class="hr"><button class="sm-btn" onclick="clearLog()">Clear</button></span>
      </div>
      <div class="pb" style="padding:7px 10px"><div id="elog"></div></div>
    </div>
  </div>

  <!-- ROW 4: Diagnostics -->
  <div class="diag">
    <h3>🔬 Diagnostics</h3>
    <div class="dg">
      <div class="di"><div class="dlbl">Backend URL</div><div class="dval" style="color:var(--blue)">http://localhost:3000</div></div>
      <div class="di" id="dbg-refresh"><div class="dlbl">Last refresh</div><div class="dval">—</div></div>
      <div class="di" id="dbg-scans">  <div class="dlbl">QR scans sent</div><div class="dval">0</div></div>
      <div class="di" id="dbg-errors"> <div class="dlbl">Errors</div><div class="dval">0</div></div>
      <div class="di" id="dbg-sensors"><div class="dlbl">Sensor mock events</div><div class="dval">0</div></div>
    </div>
  </div>

</div><!-- /main -->

<script>
  const API = 'http://localhost:3000';

  // state
  let bySpot = {};
  let scans = 0, errors = 0, sensorEvents = 0;

  // clock
  setInterval(() => {
    document.getElementById('clock').textContent = new Date().toLocaleTimeString();
  }, 1000);

  function esc(s) {
    return String(s)
      .replace(/&/g,'&amp;').replace(/</g,'&lt;')
      .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  // ── Logging ────────────────────────────────────────────────────────
  function log(msg, cls = 'info') {
    const el = document.getElementById('elog');
    const d  = document.createElement('div');
    d.className = 'le';
    d.innerHTML = `<span class="lt">${new Date().toLocaleTimeString()}</span><span class="l${cls}">${esc(msg)}</span>`;
    el.prepend(d);
    while (el.children.length > 300) el.removeChild(el.lastChild);
  }
  function clearLog() { document.getElementById('elog').innerHTML = ''; }

  // ── Pills ──────────────────────────────────────────────────────────
  function pill(id, cls, txt) {
    const el = document.getElementById(id);
    el.className = `pill ${cls}`;
    el.innerHTML = `<span class="dot"></span> ${txt}`;
  }

  // ── Diag ───────────────────────────────────────────────────────────
  function diag(id, cls, lbl, val) {
    const el = document.getElementById(id);
    if (!el) return;
    el.className = `di ${cls}`;
    el.innerHTML = `<div class="dlbl">${lbl}</div><div class="dval">${val}</div>`;
  }

  // ── fmtDur ─────────────────────────────────────────────────────────
  function fmtDur(since) {
    const s = Math.floor((Date.now() - since) / 1000);
    if (s < 60)   return `${s}s`;
    if (s < 3600) return `${Math.floor(s/60)}m ${s%60}s`;
    return `${Math.floor(s/3600)}h ${Math.floor((s%3600)/60)}m`;
  }

  // ── Refresh ────────────────────────────────────────────────────────
  async function doRefresh() {
    try {
      const r = await fetch(`${API}/parking/admin-status`);
      if (!r.ok) throw new Error(`HTTP ${r.status} ${r.statusText}`);
      const d = await r.json();

      pill('pill-api',  'ok', 'API ✓');
      pill('pill-mqtt', d.mqttConnected ? 'ok' : 'err',
           `MQTT ${d.mqttConnected ? '✓' : '✗ offline'}`);

      const { total, available, occupied } = d.stats;
      pill('pill-spots',
        occupied === total && total > 0 ? 'err' : occupied > 0 ? 'warn' : 'ok',
        `Spots ${available}/${total} free`);
      pill('pill-sess',
        d.activeSessions.length ? 'warn' : 'ok',
        `Sessions: ${d.activeSessions.length}`);
      pill('pill-users', 'idle', `Users: ${(d.users||[]).length}`);

      bySpot = {};
      d.activeSessions.forEach(s => { bySpot[s.spot.name] = s; });

      renderSpots(d.spots);
      renderSessions(d.activeSessions);
      renderUsers(d.users || [], d.activeSessions);

      diag('dbg-refresh', 'ok', 'Last refresh', new Date().toLocaleTimeString());
      if (!d.mqttConnected) log('MQTT broker not connected — check Docker', 'warn');
    } catch(e) {
      pill('pill-api', 'err', `API ✗ ${e.message}`);
      diag('dbg-refresh', 'err', 'Last refresh', `FAILED: ${e.message}`);
      log(`Refresh error: ${e.message}`, 'err');
    }
  }

  // ── Render spots ───────────────────────────────────────────────────
  function renderSpots(spots) {
    const g = document.getElementById('spots-grid');
    if (!spots?.length) {
      g.innerHTML = '<p style="color:var(--muted)">No spots configured.</p>';
      return;
    }
    g.innerHTML = spots.map(s => {
      const sess = bySpot[s.name];
      const user = sess ? sess.user.email.split('@')[0] : '';
      const sn   = esc(s.name);
      return `
        <div class="spot-card ${s.status}">
          <div class="spot-name">${sn}</div>
          <div class="spot-lbl">${s.status === 'available' ? '✓ Free' : '⬤ Occupied'}</div>
          ${user ? `<div class="spot-user">${esc(user)}</div>` : ''}
          <div class="spot-btns">
            <button class="snr-btn snr-occ"
              onclick="mockSensor('${sn}','occupied')"
              title="Simulate: IR sensor detects a car entering this spot">
              🚗 In
            </button>
            <button class="snr-btn snr-avl"
              onclick="mockSensor('${sn}','available')"
              title="Simulate: IR sensor detects the spot is now empty">
              ✓ Out
            </button>
          </div>
        </div>`;
    }).join('');
  }

  // ── Render sessions ────────────────────────────────────────────────
  function renderSessions(sessions) {
    const w = document.getElementById('sess-wrap');
    if (!sessions.length) { w.innerHTML = '<p class="empty">No active sessions</p>'; return; }
    w.innerHTML = `
      <table class="sess-table">
        <thead><tr><th>Email</th><th>Spot</th><th>Duration</th><th>Car</th></tr></thead>
        <tbody>${sessions.map(s => `
          <tr>
            <td class="ems" title="${esc(s.user.email)}">${esc(s.user.email)}</td>
            <td><span class="spill">${esc(s.spot.name)}</span></td>
            <td class="dur">${fmtDur(new Date(s.startTime))}</td>
            <td style="font-size:12px;color:var(--sub)">${esc(s.user.carColor||'—')}</td>
          </tr>`).join('')}
        </tbody>
      </table>`;
  }

  // ── Render users (mock scan panel) ─────────────────────────────────
  function renderUsers(users, activeSessions) {
    const g = document.getElementById('user-grid');
    if (!users.length) {
      g.innerHTML = '<p style="color:var(--muted);font-size:12px">No users found.</p>';
      return;
    }
    const activeEmails = new Set(activeSessions.map(s => s.user.email));
    g.innerHTML = users.map(u => {
      const parked   = activeEmails.has(u.email);
      const hasQr    = !!u.qrCode;
      const qrSafe   = esc(u.qrCode || '');
      const emailSafe= esc(u.email);
      const qrShort  = u.qrCode ? u.qrCode.slice(0,18) + '…' : '(no QR)';
      return `
        <div class="user-card">
          <div class="user-email" title="${emailSafe}">${emailSafe}</div>
          <div class="user-role">${esc(u.role || 'user')}</div>
          <div class="user-qr"   title="${qrSafe}">QR: ${esc(qrShort)}</div>
          <div class="user-status ${parked ? 'parked' : 'free'}">
            ${parked ? '⬤ Currently parked' : '✓ Not parked'}
          </div>
          <div class="user-actions">
            <button class="scan-btn entry-btn"
              ${(!hasQr || parked) ? 'disabled' : `onclick="mockScan('${qrSafe}','${emailSafe}')"`}
              title="${parked ? 'Already parked' : 'Simulate entry scan'}">
              ↪ Entry
            </button>
            <button class="scan-btn exit-btn"
              ${(!hasQr || !parked) ? 'disabled' : `onclick="mockScan('${qrSafe}','${emailSafe}')"`}
              title="${!parked ? 'No active session' : 'Simulate exit scan'}">
              ↩ Exit
            </button>
          </div>
        </div>`;
    }).join('');
  }

  // ── Mock sensor ────────────────────────────────────────────────────
  async function mockSensor(spotName, status) {
    log(`[SENSOR] Simulating ${spotName} → ${status}`, 'sensor');
    sensorEvents++;
    diag('dbg-sensors', '', 'Sensor mock events', sensorEvents);
    try {
      const r = await fetch(`${API}/parking/mock-sensor`, {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ spotName, status }),
      });
      const d = await r.json();
      if (d.ok) {
        log(`[SENSOR ✓] ${spotName} → ${status}  |  published to parking/sensor/${spotName} via MQTT`, 'sensor');
      } else {
        log(`[SENSOR ✗] ${JSON.stringify(d)}`, 'err');
        errors++;
        diag('dbg-errors', 'err', 'Errors', errors);
      }
    } catch(e) {
      log(`[SENSOR ✗] ${e.message}`, 'err');
      errors++;
      diag('dbg-errors', 'err', 'Errors', errors);
    }
    setTimeout(doRefresh, 600);
  }

  // ── Mock user scan ─────────────────────────────────────────────────
  async function mockScan(qr, email) {
    log(`[MOCK SCAN] Sending QR for ${email}`, 'scan');
    await processScan(qr);
  }

  // ── Physical scanner input ─────────────────────────────────────────
  const scannerEl = document.getElementById('scanner-input');
  const fdotEl    = document.getElementById('fdot');
  const flabelEl  = document.getElementById('flabel');
  const fbarEl    = document.getElementById('focus-bar');
  const bufEl     = document.getElementById('buf');

  function activateScanner() { scannerEl.focus(); }

  scannerEl.addEventListener('focus', () => {
    fdotEl.className  = 'fdot on';
    flabelEl.textContent = '🟢 ACTIVE — point GM65 at a QR code now';
    fbarEl.classList.add('active');
    log('GM65 scanner activated', 'info');
  });
  scannerEl.addEventListener('blur', () => {
    fdotEl.className  = 'fdot off';
    flabelEl.textContent = '🔴 INACTIVE — click here to activate';
    fbarEl.classList.remove('active');
  });
  scannerEl.addEventListener('input', () => {
    bufEl.textContent = scannerEl.value ? `buffering: ${scannerEl.value}` : '—';
  });
  scannerEl.addEventListener('keydown', async e => {
    if (e.key === 'Enter') {
      const qr = scannerEl.value.trim();
      scannerEl.value = '';
      bufEl.textContent = '—';
      if (qr) await processScan(qr);
    }
  });

  // Auto-capture keystrokes if no input is active
  document.addEventListener('keydown', e => {
    const tag = document.activeElement?.tagName;
    if (tag === 'INPUT' || tag === 'TEXTAREA') return;
    if (e.key.length === 1 && !e.ctrlKey && !e.metaKey) {
      scannerEl.focus();
      scannerEl.value += e.key;
      bufEl.textContent = `buffering: ${scannerEl.value}`;
      e.preventDefault();
    }
  });

  // Manual input
  const manualEl = document.getElementById('manual-input');
  manualEl.addEventListener('keydown', async e => {
    if (e.key === 'Enter') {
      const qr = manualEl.value.trim(); manualEl.value = '';
      if (qr) { log(`[MANUAL] ${qr}`, 'info'); await processScan(qr); }
    }
  });
  function manualSend() {
    const qr = manualEl.value.trim(); manualEl.value = '';
    if (qr) { log(`[MANUAL] ${qr}`, 'info'); processScan(qr); }
  }

  // ── Core: send scan to backend ─────────────────────────────────────
  async function processScan(qr) {
    const badge  = document.getElementById('lbadge');
    const detail = document.getElementById('last-detail');
    badge.className  = 'sbadge b-idle';
    badge.textContent = '⏳ Sending…';
    detail.textContent = qr;
    log(`[SCAN] ${qr}`, 'scan');
    scans++;
    diag('dbg-scans', '', 'QR scans sent', scans);

    try {
      const r = await fetch(`${API}/parking/hardware-scan`, {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ qrCode: qr }),
      });
      const d = await r.json();

      if (d.action === 'entrance') {
        const spot = d.session?.spot?.name ?? '?';
        badge.className  = 'sbadge b-ok';
        badge.textContent = `✓ ENTRY → ${spot}`;
        detail.textContent = `Spot ${spot} assigned — QR: ${qr}`;
        log(`[✓] ENTRY → Spot ${spot}  |  MQTT OPEN_ENTRY published to ESP32`, 'ok');
      } else if (d.action === 'exit') {
        const spot = d.session?.spot?.name ?? '?';
        badge.className  = 'sbadge b-ok';
        badge.textContent = `✓ EXIT → ${spot} freed`;
        detail.textContent = `Spot ${spot} freed — QR: ${qr}`;
        log(`[✓] EXIT → Spot ${spot} freed  |  MQTT OPEN_EXIT published to ESP32`, 'ok');
      } else if (d.statusCode || d.error) {
        badge.className  = 'sbadge b-err';
        badge.textContent = `✗ ${d.statusCode ?? 'Error'}`;
        detail.textContent = `${d.message ?? JSON.stringify(d)}  (QR: ${qr})`;
        log(`[✗] ${d.statusCode} — ${d.message}`, 'err');
        errors++;
        diag('dbg-errors', 'err', 'Errors', errors);
      } else {
        badge.className  = 'sbadge b-err';
        badge.textContent = '✗ Unexpected';
        detail.textContent = JSON.stringify(d);
        log(`[?] Unexpected response: ${JSON.stringify(d)}`, 'warn');
      }
    } catch(e) {
      badge.className  = 'sbadge b-err';
      badge.textContent = '✗ Network error';
      detail.textContent = e.message;
      log(`[✗] Network: ${e.message}`, 'err');
      errors++;
      diag('dbg-errors', 'err', 'Errors', errors);
    }

    setTimeout(doRefresh, 700);
  }

  // ── Boot ───────────────────────────────────────────────────────────
  log('Dashboard loaded. Connecting to http://localhost:3000…', 'info');
  doRefresh();
  setInterval(doRefresh, 3000);
  setTimeout(activateScanner, 400);
</script>
</body>
</html>
"""

pathlib.Path('dashboard.html').write_text(content)
print(f"Written {len(content)} bytes to dashboard.html")
