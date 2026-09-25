const SPREADSHEET_ID = '1V_ZywpcvTufLf3Sa-Br2KwuaCZ58vaVeUSbTNulZIbI';
const SHEET_NAME = 'Потенциални Клиенти Сайт';
const REGISTRATION_SHEET_NAME = 'Таблет Данни';
const EXPECTED_COLUMNS = 18;
const VISIBLE_OFFER_COLUMNS = 5;

function doPost(event) {
  const lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    const data = JSON.parse(event.postData.contents || '{}');
    const expectedSecret = PropertiesService.getScriptProperties().getProperty('AIM_WEBHOOK_SECRET');
    if (!expectedSecret || data.secret !== expectedSecret) {
      return jsonResponse({ok: false, error: 'unauthorized'});
    }

    if (data.kind === 'wat_registration') {
      return appendWatRegistration(data);
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

    const offers = Array.isArray(data.offers) ? data.offers : [];
    const offerBoxes = offers.slice(0, VISIBLE_OFFER_COLUMNS).map(formatOffer);
    while (offerBoxes.length < VISIBLE_OFFER_COLUMNS) offerBoxes.push('');
    const additionalOffers = offers
      .slice(VISIBLE_OFFER_COLUMNS)
      .map(formatOffer)
      .join('\n\n');
    const fullName = [data.first_name, data.last_name].filter(Boolean).join(' ');
    const rows = [[
      data.student_id || '',
      parseDate(data.created_at),
      safeCell(fullName),
      safeCell(data.email),
      forceText(data.phone),
      safeCell(data.university),
      safeCell(data.course),
      safeCell(data.specialty),
      safeCell(data.status),
      offers.length,
      ...offerBoxes,
      safeCell(additionalOffers),
      parseDate(data.updated_at),
      safeCell(data.inquiry_message),
    ]];
    sheet.getRange(sheet.getLastRow() + 1, 1, rows.length, EXPECTED_COLUMNS).setValues(rows);
    return jsonResponse({ok: true, rows: rows.length});
  } catch (error) {
    return jsonResponse({ok: false, error: String(error)});
  } finally {
    lock.releaseLock();
  }
}

function appendWatRegistration(data) {
  const sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(REGISTRATION_SHEET_NAME);
  if (!sheet) return jsonResponse({ok: false, error: 'registration_sheet_not_found'});
  const registrationId = String(data.registration_id || '').trim();
  const lastRow = sheet.getLastRow();
  if (registrationId && lastRow > 1) {
    const existingIds = sheet.getRange(2, 1, lastRow - 1, 1).getDisplayValues();
    if (existingIds.some(row => row[0] === registrationId)) {
      return jsonResponse({ok: true, rows: 0, duplicate: true});
    }
  }
  const row = [[
    safeCell(registrationId),
    parseDate(data.registered_at),
    safeCell(data.full_name),
    forceText(data.phone),
    safeCell(data.course),
    safeCell(data.email),
    safeCell(data.university),
    safeCell(data.notes),
    safeCell(data.source),
    safeCell(data.page),
    safeCell(data.specialty),
  ]];
  sheet.getRange(sheet.getLastRow() + 1, 1, 1, row[0].length).setValues(row);
  return jsonResponse({ok: true, rows: 1});
}

function formatOffer(offer) {
  const location = [offer.city, offer.state].filter(Boolean).join(', ');
  const wage = offer.wage === null || offer.wage === undefined || offer.wage === ''
    ? 'Заплащане по оферта'
    : '$' + Number(offer.wage).toFixed(2) + '/час';
  const details = [location, wage, offer.housing].filter(Boolean).join(' · ');
  return safeCell([
    offer.position,
    offer.employer,
    details,
    offer.url,
  ].filter(Boolean).join('\n'));
}

function safeCell(value) {
  const text = value === null || value === undefined ? '' : String(value);
  return /^[=+\-@]/.test(text.trimStart()) ? "'" + text : text;
}

function forceText(value) {
  const text = value === null || value === undefined ? '' : String(value);
  if (!text) return '';
  return "'" + text.replace(/^'/, '');
}

function parseDate(value) {
  const parsed = new Date(value);
  return isNaN(parsed.getTime()) ? '' : parsed;
}

function jsonResponse(payload) {
  return ContentService.createTextOutput(JSON.stringify(payload))
    .setMimeType(ContentService.MimeType.JSON);
}
