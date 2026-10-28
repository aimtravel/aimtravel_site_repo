(function (root) {
  'use strict';
  function failure(message, status, fields) {
    const error = new Error(message);
    error.status = status;
    error.fields = fields || {};
    return error;
  }
  async function readResponse(response) {
    const text = await response.text();
    let result;
    try { result = JSON.parse(text); } catch (_) {
      const message = response.status === 403
        ? 'Your session could not be verified. Your answers are still here. Please try submitting again.'
        : response.status === 413
          ? 'The photo is too large for the server. Please choose a smaller JPG or PNG photo.'
          : 'The server could not complete your request. Your answers are still here. Please wait a moment and submit again.';
      throw failure(message + ' (HTTP ' + response.status + ')', response.status,
        response.status === 413 ? {'profile-photo': 'Please choose a smaller JPG or PNG photo.'} : {});
    }
    if (!result || typeof result !== 'object' || Array.isArray(result)) {
      throw failure('The server returned an unexpected response. Your answers are still here. Please try again.', response.status);
    }
    if (!response.ok || result.ok !== true) {
      const message = result.error === 'rate_limited'
        ? 'An application with this email was recently submitted. Please wait a moment before trying again.'
        : typeof result.error === 'string' ? result.error : 'We could not submit your application. Please try again.';
      throw failure(message, response.status, result.fields);
    }
    return result;
  }
  async function csrfToken(fetcher) {
    const response = await fetcher('/application-form/session/', {credentials:'same-origin', cache:'no-store'});
    let result;
    try { result = JSON.parse(await response.text()); } catch (_) {
      throw failure('We could not refresh your session. Your answers are still here. Please try again. (HTTP ' + response.status + ')', response.status);
    }
    if (!response.ok || typeof result.csrfToken !== 'string' || !/^[A-Za-z0-9]{64}$/.test(result.csrfToken)) {
      throw failure('We could not verify your session. Your answers are still here. Please try again.', response.status);
    }
    return result.csrfToken;
  }
  const api = {readResponse: readResponse, csrfToken: csrfToken};
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.AIMApplicationTransport = api;
})(typeof window !== 'undefined' ? window : globalThis);
