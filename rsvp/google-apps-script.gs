/**
 * Invitații Magice Digitale — confirmări pentru toți clienții, dintr-un singur script.
 *
 * CUM FUNCȚIONEAZĂ
 * - Acest script stă în tabelul tău central („Panou confirmări”), în contul tău Google.
 * - Fila „Clienți” are câte un rând pentru fiecare invitație vândută: ID invitație, emailul clientului, numele evenimentului.
 * - Pentru fiecare client, scriptul creează un Google Sheet separat, i-l partajează pe email
 *   și îi trimite un email la fiecare confirmare nouă.
 * - Tu vezi oricum toate confirmările și în fila „Toate”.
 *
 * INSTALARE (o singură dată)
 * 1. Creezi un Google Sheet nou, de ex. „Panou confirmări”.
 * 2. Extensions → Apps Script, ștergi tot și lipești acest cod. Salvezi.
 * 3. Rulezi o dată funcția `pregatestePanoul` (alegi din listă, apoi Run) și dai permisiunile.
 * 4. Deploy → New deployment → Web app; Execute as: Me; Who has access: Anyone → Deploy.
 * 5. Copiezi „Web app URL” (se termină în /exec). Aceeași adresă se pune în TOATE invitațiile.
 *
 * PENTRU FIECARE CLIENT NOU
 * 1. În fila „Clienți” adaugi un rând: ID invitație (ex. ioana-ion-2027), emailul clientului, numele evenimentului.
 * 2. Din meniul „Invitații” → „Creează tabelul pentru clienții noi”.
 *    Clientul primește pe email accesul la tabelul lui.
 * 3. În invitația clientului, INVITATIE = același ID.
 */

const PANOU_CLIENTI = 'Clienți';
const PANOU_TOATE = 'Toate';
const ANTET = ['Data', 'Nume', 'Participă', 'Persoane', 'Mesaj'];
const COL = { id: 1, email: 2, eveniment: 3, link: 4, activ: 5 };

function onOpen() {
  SpreadsheetApp.getUi().createMenu('Invitații')
    .addItem('Creează tabelul pentru clienții noi', 'creeazaTabeleNoi')
    .addItem('Pregătește panoul', 'pregatestePanoul')
    .addToUi();
}

function pregatestePanoul() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let c = ss.getSheetByName(PANOU_CLIENTI);
  if (!c) {
    c = ss.insertSheet(PANOU_CLIENTI, 0);
    c.appendRow(['ID invitație', 'Email client', 'Eveniment', 'Tabel client (automat)', 'Activ (DA/NU)']);
    c.setFrozenRows(1); c.getRange('A1:E1').setFontWeight('bold'); c.setColumnWidths(1, 5, 220);
  }
  let t = ss.getSheetByName(PANOU_TOATE);
  if (!t) {
    t = ss.insertSheet(PANOU_TOATE);
    t.appendRow(['Data', 'ID invitație'].concat(ANTET.slice(1)));
    t.setFrozenRows(1); t.getRange('A1:F1').setFontWeight('bold');
  }
}

/* Creează tabelul și trimite accesul pentru toți clienții care nu au încă tabel. */
function creeazaTabeleNoi() {
  pregatestePanoul();
  const c = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(PANOU_CLIENTI);
  const rows = c.getLastRow() - 1;
  if (rows < 1) return;
  const data = c.getRange(2, 1, rows, 5).getValues();
  let noi = 0;
  data.forEach((r, i) => {
    if (r[COL.id - 1] && r[COL.email - 1] && !r[COL.link - 1]) { tabelClient_(c, i + 2, r); noi++; }
  });
  SpreadsheetApp.getActive().toast(noi ? 'Am creat ' + noi + ' tabel(e) noi.' : 'Nu sunt clienți noi.');
}

function tabelClient_(c, rowIndex, r) {
  const id = String(r[COL.id - 1]).trim(), email = String(r[COL.email - 1]).trim();
  const ev = String(r[COL.eveniment - 1] || id).trim();
  const ss = SpreadsheetApp.create('Confirmări — ' + ev);
  const sh = ss.getSheets()[0];
  sh.setName('Confirmări'); sh.appendRow(ANTET); sh.setFrozenRows(1); sh.getRange('A1:E1').setFontWeight('bold');
  sh.getRange('G1').setValue('Total persoane care vin:').setFontWeight('bold');
  sh.getRange('H1').setFormula('=SUMIF(C:C,"Da",D:D)');
  ss.addViewer(email); // Google îi trimite clientului un email cu acces la tabel
  c.getRange(rowIndex, COL.link).setValue(ss.getUrl());
  if (!c.getRange(rowIndex, COL.activ).getValue()) c.getRange(rowIndex, COL.activ).setValue('DA');
  return ss;
}

function doPost(e) {
  const p = (e && e.parameter) || {};
  if (p.website) return ok_(); // capcană pentru roboți

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
    const data = c.getRange(2, 1, n, 5).getValues();
    const idx = data.findIndex(r => String(r[COL.id - 1]).trim() === id);
    if (idx < 0) return ok_();                                    // invitație necunoscută: ignorăm
    const r = data[idx];
    if (String(r[COL.activ - 1]).toUpperCase() === 'NU') return ok_(); // invitație oprită

    const row = [new Date(), clean(p.nume), clean(p.participa), Number(p.persoane) || 0, clean(p.mesaj)];

    let link = r[COL.link - 1];
    const client = link ? SpreadsheetApp.openByUrl(link) : tabelClient_(c, idx + 2, r);
    client.getSheets()[0].appendRow(row);
    panou.getSheetByName(PANOU_TOATE).appendRow([row[0], id, row[1], row[2], row[3], row[4]]);

    const email = String(r[COL.email - 1]).trim();
    if (email) {
      const sh = client.getSheets()[0];
      const vals = sh.getLastRow() > 1 ? sh.getRange(2, 3, sh.getLastRow() - 1, 2).getValues() : [];
      const vin = vals.reduce((s, v) => s + (v[0] === 'Da' ? Number(v[1]) || 0 : 0), 0);
      MailApp.sendEmail({
        to: email,
        name: 'Invitații Magice Digitale',
        subject: 'Confirmare nouă: ' + row[1] + ' (' + row[2] + ')',
        body: 'Ați primit o confirmare nouă pentru ' + (r[COL.eveniment - 1] || id) + ':\n\n' +
              'Nume: ' + row[1] + '\nParticipă: ' + row[2] + '\nPersoane: ' + row[3] + '\nMesaj: ' + (row[4] || '-') +
              '\n\nTotal persoane confirmate până acum: ' + vin +
              '\nToate confirmările: ' + client.getUrl() + '\n\nCu drag,\nInvitații Magice Digitale'
      });
    }
  } finally {
    lock.releaseLock();
  }
  return ok_();
}

function ok_() {
  return ContentService.createTextOutput(JSON.stringify({ ok: true })).setMimeType(ContentService.MimeType.JSON);
}
