const assert = require('node:assert/strict');
const transport = require('../static/js/application-form-transport.js');
function response(status, body) {
  return {status, ok:status >= 200 && status < 300, text:async()=>body,
    json:async()=>{throw new Error('Safari raw JSON parser must not be called');}};
}
(async()=>{
  assert.equal((await transport.readResponse(response(200,'{"ok":true}'))).ok,true);
  await assert.rejects(()=>transport.readResponse(response(403,'<html>Forbidden</html>')),
    e=>e.status===403 && /session/i.test(e.message) && !e.message.includes('expected pattern'));
  await assert.rejects(()=>transport.readResponse(response(503,'<html>Unavailable</html>')),
    e=>/HTTP 503/.test(e.message));
  await assert.rejects(()=>transport.readResponse(response(200,'')), e=>/server/.test(e.message));
  await assert.rejects(()=>transport.readResponse(response(413,'Too large')),
    e=>!!e.fields['profile-photo']);
  await assert.rejects(()=>transport.readResponse(response(400,'{"ok":false,"error":"Invalid email","fields":{"email":"Check email"}}')),
    e=>e.message==='Invalid email' && e.fields.email==='Check email');
  const token='a'.repeat(64);
  const received=await transport.csrfToken(async(url,options)=>{
    assert.equal(url,'/application-form/session/'); assert.equal(options.cache,'no-store');
    assert.equal(options.credentials,'same-origin'); return response(200,JSON.stringify({csrfToken:token}));
  });
  assert.equal(received,token);
  await assert.rejects(()=>transport.csrfToken(async()=>response(403,'<html>Forbidden</html>')), /HTTP 403/);
  console.log('Application Form transport: Safari HTML errors, HTTP status, fields and fresh CSRF tests passed.');
})().catch(error=>{console.error(error);process.exitCode=1;});
