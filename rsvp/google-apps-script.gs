/**
 * Confirmări pentru Invitații Magice Digitale → Google Sheets
 *
 * Instalare (o singură dată):
 * 1. Creezi un Google Sheet nou (ex. „Confirmări invitații”).
 * 2. Extensions → Apps Script, ștergi tot și lipești acest cod.
 * 3. Opțional: scrii adresa de email a mirilor la NOTIFY_EMAIL ca să primească un mail la fiecare confirmare.
 * 4. Deploy → New deployment → tip „Web app”; Execute as: Me; Who has access: Anyone → Deploy, apoi Authorize access.
 * 5. Copiezi adresa „Web app URL” (se termină în /exec) și o pui în invitație la RSVP_URL.
 *
 * Fiecare invitație primește automat propria filă (tab), după valoarea INVITATIE din pagină.
 */
const NOTIFY_EMAIL = ''; // ex. 'mirii@gmail.com'; lasă gol dacă nu vrei email

function doPost(e) {
  const p = (e && e.parameter) || {};
  if (p.website) return ok_(); // câmp capcană pentru roboți

  const clean = v => {
    v = String(v || '').slice(0, 1000).trim();
    return /^[=+\-@]/.test(v) ? "'" + v : v; // previne formule în celule
  };

  const lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const tab = clean(p.invitatie || 'Confirmări').replace(/^'/, '').slice(0, 90) || 'Confirmări';
    let sh = ss.getSheetByName(tab);
    if (!sh) {
      sh = ss.insertSheet(tab);
      sh.appendRow(['Data', 'Nume', 'Participă', 'Persoane', 'Mesaj']);
      sh.setFrozenRows(1);
      sh.getRange('A1:E1').setFontWeight('bold');
    }
    const row = [new Date(), clean(p.nume), clean(p.participa), Number(p.persoane) || 0, clean(p.mesaj)];
    sh.appendRow(row);

    if (NOTIFY_EMAIL) {
      MailApp.sendEmail(NOTIFY_EMAIL,
        'Confirmare nouă: ' + row[1] + ' (' + row[2] + ')',
        'Invitație: ' + tab + '\nNume: ' + row[1] + '\nParticipă: ' + row[2] +
        '\nPersoane: ' + row[3] + '\nMesaj: ' + (row[4] || '-') + '\n\nToate confirmările: ' + ss.getUrl());
    }
  } finally {
    lock.releaseLock();
  }
  return ok_();
}

function ok_() {
  return ContentService.createTextOutput(JSON.stringify({ ok: true })).setMimeType(ContentService.MimeType.JSON);
}
