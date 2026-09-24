const SPREADSHEET_ID = '1V_ZywpcvTufLf3Sa-Br2KwuaCZ58vaVeUSbTNulZIbI';
const SHEET_NAME = 'Потенциални Клиенти Сайт';
const EXPECTED_COLUMNS = 20;

function doPost(event) {
  const lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    const data = JSON.parse(event.postData.contents || '{}');
    const expectedSecret = PropertiesService.getScriptProperties().getProperty('AIM_WEBHOOK_SECRET');
    if (!expectedSecret || data.secret !== expectedSecret) {
      return jsonResponse({ok: false, error: 'unauthorized'});
    }

    const sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(SHEET_NAME);
    if (!sheet) return jsonResponse({ok: false, error: 'sheet_not_found'});

    const studentId = String(data.student_id || '');
    const lastRow = sheet.getLastRow();
    if (lastRow > 1) {
      const ids = sheet.getRange(2, 1, lastRow - 1, 1).getDisplayValues();
      for (let index = ids.length - 1; index >= 0; index--) {
        if (ids[index][0] === studentId) sheet.deleteRow(index + 2);
      }
    }

    const offers = Array.isArray(data.offers) && data.offers.length ? data.offers : [{}];
    const rows = offers.map(offer => [
      data.student_id || '',
      parseDate(data.created_at),
      safeCell(data.first_name),
      safeCell(data.last_name),
      safeCell(data.email),
      safeCell(data.phone),
      safeCell(data.university),
      safeCell(data.course),
      safeCell(data.specialty),
      safeCell(data.status),
      offer.id || '',
      safeCell(offer.employer),
      safeCell(offer.position),
      safeCell(offer.city),
      safeCell(offer.state),
      offer.wage === null || offer.wage === undefined ? '' : Number(offer.wage),
      safeCell(offer.housing),
      safeCell(offer.url),
      parseDate(data.updated_at),
      '',
    ]);
    sheet.getRange(sheet.getLastRow() + 1, 1, rows.length, EXPECTED_COLUMNS).setValues(rows);
    return jsonResponse({ok: true, rows: rows.length});
  } catch (error) {
    return jsonResponse({ok: false, error: String(error)});
  } finally {
    lock.releaseLock();
  }
}

function safeCell(value) {
  const text = value === null || value === undefined ? '' : String(value);
  return /^[=+\-@]/.test(text.trimStart()) ? "'" + text : text;
}

function parseDate(value) {
  const parsed = new Date(value);
  return isNaN(parsed.getTime()) ? '' : parsed;
}

function jsonResponse(payload) {
  return ContentService.createTextOutput(JSON.stringify(payload))
    .setMimeType(ContentService.MimeType.JSON);
}
