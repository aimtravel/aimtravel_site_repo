
// Online registration export. Called only after the existing secret check,
// while doPost holds its existing ScriptLock. The last column belongs to AIM staff.
function upsertOnlineRegistration_(body) {
  const id = String(body.registrationId || '');
  const values = body.values;
  if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(id) ||
      !Array.isArray(values) || values.length !== 20 || values[19] !== id) {
    return json_({ok:false, error:'invalid_registration'});
  }
  const numeric = [6,7,8,9,11,12,13];
  for (let i = 0; i < values.length; i++) {
    if (numeric.indexOf(i) !== -1) {
      if (!Number.isSafeInteger(values[i]) || values[i] < 0 || values[i] > 100000) return json_({ok:false, error:'invalid_amount'});
    } else if (typeof values[i] !== 'string' || values[i].length > 1000) {
      return json_({ok:false, error:'invalid_field'});
    }
  }
  const sheet = SpreadsheetApp.openById('1-D3RRDoeixPiejumVTymNs9Xnplv4LPz6F3tNQwOehE').getSheetByName('Записани онлайн');
  if (!sheet) return json_({ok:false, error:'sheet_not_ready'});
  // Accept both layouts during rollout; the existing wire payload stays compatible.
  const idColumn = sheet.getRange(1,20).getValue() === 'ID регистрация' ? 20 :
    sheet.getRange(1,19).getValue() === 'ID регистрация' ? 19 : 0;
  if (!idColumn) return json_({ok:false, error:'sheet_not_ready'});
  const last = sheet.getLastRow();
  const existing = last > 1 ? sheet.getRange(2,idColumn,last-1,1).createTextFinder(id).matchEntireCell(true).findNext() : null;
  const row = existing ? existing.getRow() : last + 1;
  if (row > sheet.getMaxRows()) sheet.insertRowsAfter(sheet.getMaxRows(),100);
  const safe = values.map(function(value,i) {
    if (numeric.indexOf(i) !== -1) return value;
    return /^[=+@-]/.test(value) ? "'" + value : value;
  });
  const output = idColumn === 19 ? safe.filter(function(value,index) {return index !== 7;}) : safe;
  const range = sheet.getRange(row,1,1,idColumn);
  range.setNumberFormat('@');
  range.setValues([output]);
  sheet.getRange(row,7).setNumberFormat('0');
  sheet.getRange(row,8,1,idColumn === 19 ? 2 : 3).setNumberFormat('#,##0.00');
  sheet.getRange(row,idColumn === 19 ? 11 : 12,1,3).setNumberFormat('#,##0.00');
  SpreadsheetApp.flush();
  return json_({ok:true, registrationId:id});
}
