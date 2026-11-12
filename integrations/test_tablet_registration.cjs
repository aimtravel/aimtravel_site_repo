const vm = require('node:vm');
const fs = require('node:fs');
const assert = require('node:assert/strict');
let acquired = false, releases = 0, flushes = 0;
const rows = [['header']];
const sheet = {getLastRow: () => rows.length, getRange: (row, col, count) => ({
  getDisplayValues: () => rows.slice(row - 1, row - 1 + count).map(r => [r[0]]),
  setValues: values => { for (const value of values) rows.push(value); },
})};
const context = {
  LockService: {getScriptLock: () => ({tryLock: ms => {assert.equal(ms, 5000); return acquired;}, releaseLock: () => releases++})},
  PropertiesService: {getScriptProperties: () => ({getProperty: () => 'test-only-secret'})},
  SpreadsheetApp: {openById: () => ({getSheetByName: () => sheet}), flush: () => flushes++},
  ContentService: {MimeType: {JSON: 'json'}, createTextOutput: value => ({setMimeType: () => JSON.parse(value)})},
};
vm.createContext(context);
vm.runInContext(fs.readFileSync(__dirname + '/tablet_registration_receiver.gs', 'utf8'), context);
const payload = {secret: 'test-only-secret', kind: 'wat_registration', registration_id: 'test-tablet-id', full_name: 'TEST ONLY'};
const event = {postData: {contents: JSON.stringify(payload)}};
assert.equal(context.doPost(event).error, 'busy');
assert.equal(rows.length, 1);
acquired = true;
assert.equal(context.doPost(event).ok, true);
assert.equal(flushes, 1);
assert.equal(context.doPost(event).duplicate, true);
assert.equal(rows.length, 2);
assert.equal(releases, 2);
console.log('Receiver busy, successful flush and duplicate-ID checks passed.');
