/**
 * Invitații Magice Digitale — confirmări pentru toți clienții, dintr-un singur script.
 *
 * CUM FUNCȚIONEAZĂ
 * - Acest script stă în tabelul tău central („Panou confirmări”), în contul tău Google.
 * - Fila „Clienți” e panoul tău de gestiune: câte un rând pentru fiecare invitație vândută,
 *   cu linkul invitației, tabelul clientului, numărul de confirmări și starea (activă sau oprită).
 * - Pentru fiecare client, scriptul creează un Google Sheet separat, i-l partajează pe email
 *   și îi trimite un email la fiecare confirmare nouă.
 * - Tu vezi toate confirmările în fila „Toate” și, separat, în câte o filă pentru fiecare invitație,
 *   cu numele egal cu ID-ul invitației (se creează singură).
 *
 * INSTALARE (o singură dată)
 * 1. Creezi un Google Sheet nou, de ex. „Panou confirmări”.
 * 2. Extensions → Apps Script, ștergi tot și lipești acest cod. Salvezi.
 * 3. Rulezi o dată funcția `pregatestePanoul` (alegi din listă, apoi Run) și dai permisiunile.
 * 4. Deploy → New deployment → Web app; Execute as: Me; Who has access: Anyone → Deploy.
 * 5. Copiezi „Web app URL” (se termină în /exec). Aceeași adresă se pune în TOATE invitațiile.
 * La orice modificare a codului: Deploy → Manage deployments → Edit → Version: New version → Deploy.
 *
 * PENTRU FIECARE CLIENT NOU
 * 1. În fila „Clienți” adaugi un rând: ID invitație (ex. ioana-ion-2027), emailul clientului, numele evenimentului.
 * 2. Din meniul „Invitații” → „Creează tabelul pentru clienții noi”.
 *    Clientul primește pe email accesul la tabelul lui, iar în rând apar linkul invitației și al tabelului.
 * 3. În invitația clientului, INVITATIE = același ID (folderul invitatii/<ID>/ de pe site).
 * 4. După eveniment scrii NU în coloana „Activ”: invitația nu mai primește confirmări.
 *
 * PLANIFICATORUL DE MESE
 * - Fiecare client are un link privat (coloana „Plan mese”), cu o cheie secretă.
 * - Pagina e pe site (invitatiimagiceonline.ro/planificator/) și citește/salvează prin acest script.
 * - Planul se salvează în tabelul clientului: fila „Mese” (lista pe mese) și fila ascunsă „_plan” (datele).
 */

const PANOU_CLIENTI = 'Clienți';
const PANOU_TOATE = 'Toate';
const SITE_INVITATII = 'https://invitatiimagiceonline.ro/invitatii/';
const SITE_PLAN = 'https://invitatiimagiceonline.ro/planificator/';
const ANTET = ['Data', 'Nume', 'Participă', 'Persoane', 'Mesaj'];
const ANTET_CLIENTI = ['ID invitație', 'Email client', 'Eveniment', 'Tabel client (automat)', 'Activ (DA/NU)',
                       'Link invitație (automat)', 'Confirmări (automat)', 'Persoane care vin (automat)', 'Ultima confirmare (automat)', 'Note',
                       'Plan mese (link privat)', 'Cheie plan (automat)'];
const COL = { id: 1, email: 2, eveniment: 3, link: 4, activ: 5, invitatie: 6, nr: 7, persoane: 8, ultima: 9, note: 10, plan: 11, cheie: 12 };
const NCOL = ANTET_CLIENTI.length;

function onOpen() {
  SpreadsheetApp.getUi().createMenu('Invitații')
    .addItem('Creează tabelul pentru clienții noi', 'creeazaTabeleNoi')
    .addItem('Actualizează linkurile și statisticile', 'actualizeazaPanoul')
    .addSeparator()
    .addItem('Pregătește panoul', 'pregatestePanoul')
    .addToUi();
}

function pregatestePanoul() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let c = ss.getSheetByName(PANOU_CLIENTI);
  if (!c) { c = ss.insertSheet(PANOU_CLIENTI, 0); }
  // antetul complet (completează și coloanele noi la un panou mai vechi)
  if (c.getRange(1, NCOL).getValue() !== ANTET_CLIENTI[NCOL - 1]) {
    c.getRange(1, 1, 1, NCOL).setValues([ANTET_CLIENTI]).setFontWeight('bold').setBackground('#f3e8d6');
    c.setFrozenRows(1); c.setFrozenColumns(1);
    c.setColumnWidth(1, 170); c.setColumnWidth(2, 210); c.setColumnWidth(3, 170); c.setColumnWidth(4, 190);
    c.setColumnWidth(5, 95); c.setColumnWidth(6, 330); c.setColumnWidths(7, 3, 150); c.setColumnWidth(10, 240); c.setColumnWidth(11, 330); c.setColumnWidth(12, 130);
  }
  let t = ss.getSheetByName(PANOU_TOATE);
  if (!t) {
    t = ss.insertSheet(PANOU_TOATE);
    t.appendRow(['Data', 'ID invitație'].concat(ANTET.slice(1)));
    t.setFrozenRows(1); t.getRange('A1:F1').setFontWeight('bold');
  }
}

/* Fila din panou pentru o invitație: numele filei = ID-ul invitației. O creează dacă lipsește. */
function filaInvitatie_(panou, id) {
  const nume = String(id).trim().slice(0, 99);
  let f = panou.getSheetByName(nume);
  if (!f) {
    f = panou.insertSheet(nume, panou.getSheets().length);
    f.appendRow(ANTET); f.setFrozenRows(1); f.getRange('A1:E1').setFontWeight('bold').setBackground('#f3e8d6');
    f.getRange('G1').setValue('Total persoane care vin:').setFontWeight('bold');
    f.getRange('H1').setValue(0).setFontWeight('bold');
    f.setColumnWidth(1, 150); f.setColumnWidth(2, 200); f.setColumnWidth(5, 320);
  }
  return f;
}

/* ID-ul din panoul Clienți devine link spre fila invitației. */
function leagaIdDeFila_(c, rowIndex, id, fila) {
  const url = '#gid=' + fila.getSheetId();
  c.getRange(rowIndex, COL.id).setRichTextValue(SpreadsheetApp.newRichTextValue().setText(String(id)).setLinkUrl(url).build());
}

/* Rescrie fila invitației cu toate confirmările din tabelul clientului. */
function sincronizeazaFila_(fila, client, total) {
  const src = client.getSheets()[0];
  const n = src.getLastRow() - 1;
  if (fila.getLastRow() > 1) fila.getRange(2, 1, fila.getLastRow() - 1, 5).clearContent();
  if (n > 0) {
    fila.getRange(2, 1, n, 5).setValues(src.getRange(2, 1, n, 5).getValues());
    fila.getRange(2, 1, n, 1).setNumberFormat('dd.mm.yyyy hh:mm');
  }
  fila.getRange('H1').setValue(total);
}

/* Linkul public al invitației, construit din ID (folderul de pe site). */
function linkInvitatie_(id) { return SITE_INVITATII + encodeURIComponent(String(id).trim()) + '/'; }
function scrieLink_(range, url) {
  range.setRichTextValue(SpreadsheetApp.newRichTextValue().setText(url).setLinkUrl(url).build());
}

/* Creează tabelul și trimite accesul pentru toți clienții care nu au încă tabel. */
function creeazaTabeleNoi() {
  pregatestePanoul();
  const c = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(PANOU_CLIENTI);
  const rows = c.getLastRow() - 1;
  if (rows < 1) return;
  const data = c.getRange(2, 1, rows, NCOL).getValues();
  let noi = 0;
  data.forEach((r, i) => {
    if (r[COL.id - 1] && r[COL.email - 1] && !r[COL.link - 1]) { tabelClient_(c, i + 2, r); noi++; }
  });
  actualizeazaPanoul(true);
  SpreadsheetApp.getActive().toast(noi ? 'Am creat ' + noi + ' tabel(e) noi.' : 'Nu sunt clienți noi.');
}

function tabelClient_(c, rowIndex, r) {
  const id = String(r[COL.id - 1]).trim(), email = String(r[COL.email - 1]).trim();
  const ev = String(r[COL.eveniment - 1] || id).trim();
  const ss = SpreadsheetApp.create('Confirmări — ' + ev);
  const sh = ss.getSheets()[0];
  sh.setName('Confirmări'); sh.appendRow(ANTET); sh.setFrozenRows(1); sh.getRange('A1:E1').setFontWeight('bold');
  sh.getRange('G1').setValue('Total persoane care vin:').setFontWeight('bold');
  sh.getRange('H1').setValue(0).setFontWeight('bold'); // totalul se actualizează din script la fiecare confirmare
  ss.addViewer(email); // Google îi trimite clientului un email cu acces la tabel
  c.getRange(rowIndex, COL.link).setValue(ss.getUrl());
  if (!c.getRange(rowIndex, COL.activ).getValue()) c.getRange(rowIndex, COL.activ).setValue('DA');
  scrieLink_(c.getRange(rowIndex, COL.invitatie), linkInvitatie_(id));
  leagaIdDeFila_(c, rowIndex, id, filaInvitatie_(c.getParent(), id));
  asiguraPlan_(c, rowIndex, id, '');
  return ss;
}

/* Statisticile unui client, citite din tabelul lui: câte confirmări, câte persoane vin, ultima confirmare. */
function statistici_(client) {
  const sh = client.getSheets()[0];
  const n = sh.getLastRow() - 1;
  if (n < 1) return { nr: 0, vin: 0, ultima: '' };
  const vals = sh.getRange(2, 1, n, 4).getValues();
  let vin = 0, ultima = '';
  vals.forEach(v => {
    if (v[2] === 'Da') vin += Number(v[3]) || 0;
    if (v[0] instanceof Date && (!ultima || v[0] > ultima)) ultima = v[0];
  });
  return { nr: n, vin: vin, ultima: ultima };
}

function scrieStatistici_(c, rowIndex, st) {
  c.getRange(rowIndex, COL.nr, 1, 3).setValues([[st.nr, st.vin, st.ultima]]);
  if (st.ultima) c.getRange(rowIndex, COL.ultima).setNumberFormat('dd.mm.yyyy hh:mm');
}

/* Completează linkurile invitațiilor și recalculează statisticile pentru toți clienții. */
function actualizeazaPanoul(tacut) {
  pregatestePanoul();
  const c = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(PANOU_CLIENTI);
  const rows = c.getLastRow() - 1;
  if (rows < 1) return;
  const data = c.getRange(2, 1, rows, NCOL).getValues();
  data.forEach((r, i) => {
    const id = String(r[COL.id - 1]).trim();
    if (!id) return;
    const row = i + 2;
    if (!r[COL.invitatie - 1]) scrieLink_(c.getRange(row, COL.invitatie), linkInvitatie_(id));
    const fila = filaInvitatie_(c.getParent(), id);
    leagaIdDeFila_(c, row, id, fila);
    if (r[COL.link - 1]) asiguraPlan_(c, row, id, r[COL.cheie - 1]);
    if (r[COL.link - 1]) {
      try {
        const client = SpreadsheetApp.openByUrl(r[COL.link - 1]);
        const st = statistici_(client);
        scrieStatistici_(c, row, st);
        sincronizeazaFila_(fila, client, st.vin);
      } catch (e) {}
    }
    const activ = String(r[COL.activ - 1]).toUpperCase() === 'NU';
    c.getRange(row, 1, 1, NCOL).setBackground(activ ? '#eeeeee' : null).setFontColor(activ ? '#888888' : null);
  });
  if (tacut !== true) SpreadsheetApp.getActive().toast('Panoul e actualizat.');
}

function doPost(e) {
  const p = (e && e.parameter) || {};
  if (p.website) return ok_(); // capcană pentru roboți
  if (p.action === 'plan') return salveazaPlan_(p);

  const clean = v => { v = String(v || '').slice(0, 1000).trim(); return /^[=+\-@]/.test(v) ? "'" + v : v; };
  const id = String(p.invitatie || '').trim();
  if (!id) return ok_();

  const lock = LockService.getScriptLock();
  lock.waitLock(15000);
  try {
    pregatestePanoul();
    const panou = SpreadsheetApp.getActiveSpreadsheet();
    const c = panou.getSheetByName(PANOU_CLIENTI);
    const n = c.getLastRow() - 1;
    if (n < 1) return ok_();
    const data = c.getRange(2, 1, n, NCOL).getValues();
    const idx = data.findIndex(r => String(r[COL.id - 1]).trim() === id);
    if (idx < 0) return ok_();                                    // invitație necunoscută: ignorăm
    const r = data[idx];
    if (String(r[COL.activ - 1]).toUpperCase() === 'NU') return ok_(); // invitație oprită

    const row = [new Date(), clean(p.nume), clean(p.participa), Number(p.persoane) || 0, clean(p.mesaj)];

    const link = r[COL.link - 1];
    const client = link ? SpreadsheetApp.openByUrl(link) : tabelClient_(c, idx + 2, r);
    const sh = client.getSheets()[0];
    sh.appendRow(row);
    panou.getSheetByName(PANOU_TOATE).appendRow([row[0], id, row[1], row[2], row[3], row[4]]);

    const st = statistici_(client);
    sh.getRange('H1').setValue(st.vin);
    const fila = filaInvitatie_(panou, id);
    fila.appendRow(row);
    fila.getRange(fila.getLastRow(), 1).setNumberFormat('dd.mm.yyyy hh:mm');
    fila.getRange('H1').setValue(st.vin);
    scrieStatistici_(c, idx + 2, st);
    if (!r[COL.invitatie - 1]) scrieLink_(c.getRange(idx + 2, COL.invitatie), linkInvitatie_(id));

    const email = String(r[COL.email - 1]).trim();
    if (email) {
      MailApp.sendEmail({
        to: email,
        name: 'Invitații Magice Digitale',
        subject: 'Confirmare nouă: ' + row[1] + ' (' + row[2] + ')',
        body: 'Ați primit o confirmare nouă pentru ' + (r[COL.eveniment - 1] || id) + ':\n\n' +
              'Nume: ' + row[1] + '\nParticipă: ' + row[2] + '\nPersoane: ' + row[3] + '\nMesaj: ' + (row[4] || '-') +
              '\n\nTotal persoane confirmate până acum: ' + st.vin +
              '\nToate confirmările: ' + client.getUrl() +
              (r[COL.cheie - 1] ? '\nPlanificați mesele: ' + linkPlan_(id, r[COL.cheie - 1]) : '') +
              '\n\nCu drag,\nInvitații Magice Digitale'
      });
    }
  } finally {
    lock.releaseLock();
  }
  return ok_();
}

/* ===================== PLANIFICATORUL DE MESE ===================== */

function linkPlan_(id, cheie) { return SITE_PLAN + '?id=' + encodeURIComponent(id) + '&k=' + encodeURIComponent(cheie); }

/* Fiecare client primește o cheie secretă și linkul privat spre planificator. */
function asiguraPlan_(c, rowIndex, id, cheie) {
  if (!cheie) {
    cheie = Utilities.getUuid().replace(/-/g, '').slice(0, 16);
    c.getRange(rowIndex, COL.cheie).setValue(cheie);
  }
  scrieLink_(c.getRange(rowIndex, COL.plan), linkPlan_(id, cheie));
}

/* Găsește clientul după ID și verifică cheia. */
function clientDupaCheie_(id, cheie) {
  const c = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(PANOU_CLIENTI);
  const n = c.getLastRow() - 1;
  if (n < 1 || !id || !cheie) return null;
  const data = c.getRange(2, 1, n, NCOL).getValues();
  const r = data.find(x => String(x[COL.id - 1]).trim() === String(id).trim());
  if (!r || !r[COL.link - 1] || String(r[COL.cheie - 1]) !== String(cheie)) return null;
  return { r: r, client: SpreadsheetApp.openByUrl(r[COL.link - 1]) };
}

/* Familiile care au confirmat cu „Da”: cheie stabilă = data confirmării + nume. */
function invitatiConfirmati_(client) {
  const sh = client.getSheets()[0];
  const n = sh.getLastRow() - 1;
  if (n < 1) return [];
  return sh.getRange(2, 1, n, 5).getValues()
    .filter(v => v[2] === 'Da' && v[1])
    .map(v => ({ key: (v[0] instanceof Date ? v[0].getTime() : String(v[0])) + '|' + v[1], nume: String(v[1]), n: Number(v[3]) || 1, mesaj: String(v[4] || '') }));
}

function citestePlan_(client) {
  const sh = client.getSheetByName('_plan');
  if (!sh || sh.getLastRow() < 1) return null;
  const parts = sh.getRange(1, 1, sh.getLastRow(), 1).getValues().map(x => x[0]).join('');
  try { return JSON.parse(parts); } catch (e) { return null; }
}

function scriePlan_(client, json) {
  let sh = client.getSheetByName('_plan');
  if (!sh) { sh = client.insertSheet('_plan'); sh.hideSheet(); }
  sh.clearContents();
  const bucati = [];
  for (let i = 0; i < json.length; i += 45000) bucati.push([json.slice(i, i + 45000)]);
  if (bucati.length) sh.getRange(1, 1, bucati.length, 1).setValues(bucati);
}

/* Fila „Mese”: lista ușor de citit, gata de trimis la restaurant. */
function scrieMese_(client, plan, invitati) {
  let sh = client.getSheetByName('Mese');
  if (!sh) { sh = client.insertSheet('Mese', 1); }
  sh.clear();
  const dupaCheie = {};
  invitati.forEach(g => { dupaCheie[g.key] = g; });
  (plan.manual || []).forEach(g => { dupaCheie[g.key] = g; });
  const rows = [['Masa', 'Locuri', 'Ocupate', 'Invitați']];
  const asezati = {};
  (plan.tables || []).forEach(t => {
    const lista = (plan.assign || []).filter(a => a.t === t.id && dupaCheie[a.g]);
    let ocupate = 0;
    const nume = lista.map(a => { ocupate += a.n; asezati[a.g] = (asezati[a.g] || 0) + a.n; return dupaCheie[a.g].nume + ' (' + a.n + ')'; });
    rows.push([t.name || 'Masă', t.seats || 0, ocupate, nume.join(', ')]);
  });
  const neasezati = Object.keys(dupaCheie).map(k => dupaCheie[k]).filter(g => (asezati[g.key] || 0) < g.n)
    .map(g => g.nume + ' (' + (g.n - (asezati[g.key] || 0)) + ')');
  rows.push(['', '', '', '']);
  rows.push(['Neașezați', '', '', neasezati.join(', ') || '—']);
  sh.getRange(1, 1, rows.length, 4).setValues(rows);
  sh.getRange('A1:D1').setFontWeight('bold').setBackground('#f3e8d6');
  sh.getRange(rows.length, 1).setFontWeight('bold');
  sh.setColumnWidth(1, 160); sh.setColumnWidth(4, 600); sh.setFrozenRows(1);
  sh.getRange(2, 4, rows.length, 1).setWrap(true);
}

/* GET: planificatorul cere invitații și planul salvat. */
function doGet(e) {
  const p = (e && e.parameter) || {};
  if (p.action !== 'plan') return ok_();
  const found = clientDupaCheie_(p.id, p.k);
  if (!found) return json_({ ok: false, error: 'Link invalid' });
  return json_({ ok: true, eveniment: String(found.r[COL.eveniment - 1] || p.id),
                 invitati: invitatiConfirmati_(found.client), plan: citestePlan_(found.client) });
}

/* POST: salvează planul trimis de planificator. */
function salveazaPlan_(p) {
  const lock = LockService.getScriptLock();
  lock.waitLock(15000);
  try {
    const found = clientDupaCheie_(p.id, p.k);
    if (!found) return json_({ ok: false, error: 'Link invalid' });
    const txt = String(p.data || '');
    if (txt.length > 400000) return json_({ ok: false, error: 'Plan prea mare' });
    const plan = JSON.parse(txt);
    scriePlan_(found.client, JSON.stringify(plan));
    scrieMese_(found.client, plan, invitatiConfirmati_(found.client));
    return json_({ ok: true, salvat: new Date().toISOString() });
  } catch (err) {
    return json_({ ok: false, error: String(err) });
  } finally {
    lock.releaseLock();
  }
}

function json_(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}

function ok_() {
  return ContentService.createTextOutput(JSON.stringify({ ok: true })).setMimeType(ContentService.MimeType.JSON);
}
