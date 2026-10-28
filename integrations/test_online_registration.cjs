const {readFileSync} = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const rows = [['header']]; rows[0][19] = 'ID регистрация';
let maxRows = 2;
const sheet = {
  getLastRow: () => rows.length,
  getMaxRows: () => maxRows,
  insertRowsAfter: (_, n) => { maxRows += n; },
  getRange(row, column, height = 1, width = 1) {
    return {
      getValue: () => rows[row-1]?.[column-1],
      setNumberFormat() { return this; },
      setValues(values) { rows[row-1] ||= []; for(let i=0;i<width;i++) rows[row-1][column-1+i] = values[0][i]; },
      createTextFinder(id) { return {matchEntireCell() { return this; }, findNext() {
        const i = rows.findIndex((v, i) => i > 0 && v[column-1] === id);
        return i < 0 ? null : {getRow: () => i+1};
      }}; }
    };
  }
};
const context = {SpreadsheetApp:{openById:()=>({getSheetByName:()=>sheet}),flush(){}}, json_: x=>x};
vm.createContext(context);
vm.runInContext(readFileSync(__dirname+'/online_registration.gs','utf8'),context);
const id='00000000-0000-4000-8000-000000000001';
const values=['28.10.2026 12:00','=unsafe','example@example.com','+359888000000','Full','AIM-TEST',2027,1699,80,1619,'Да',249,481,1868,'https://aimtravel.bg/admin/','Изпратен','Изпратено','Договорът е издаден','https://aimtravel.bg',id];
assert.equal(context.upsertOnlineRegistration_({registrationId:id,values}).ok,true);
assert.equal(rows[1][1],"'=unsafe"); assert.equal(rows[1][3],"'+359888000000");
assert.equal(rows[1][9],1619); rows[1][20]='Staff note';
assert.equal(context.upsertOnlineRegistration_({registrationId:id,values}).ok,true);
assert.equal(rows.length,2); assert.equal(rows[1][20],'Staff note');
const second='00000000-0000-4000-8000-000000000002';
assert.equal(context.upsertOnlineRegistration_({registrationId:second,values:values.map((v,i)=>i===19?second:v)}).ok,true);
assert.equal(rows.length,3); assert.equal(maxRows,102);
assert.equal(context.upsertOnlineRegistration_({registrationId:id,values:values.map((v,i)=>i===9?'=1':v)}).ok,false);
// Removing the base-fee column must preserve mapping, identifiers and staff notes.
for (const row of rows) row.splice(7,1);
assert.equal(context.upsertOnlineRegistration_({registrationId:id,values}).ok,true);
assert.equal(rows.length,3); assert.equal(rows[1][8],1619);
assert.equal(rows[1][18],id); assert.equal(rows[1][19],'Staff note');
console.log('Apps Script: upsert, separate applicants, notes, formula escaping and amount validation passed.');
