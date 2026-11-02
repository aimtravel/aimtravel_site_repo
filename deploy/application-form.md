# Public application form

`/application-form/` preserves the working testpetar form, its JSON submission
format, Word CV generation, and existing Google Apps Script delivery. It does not
replace `/zapisvane-za-brigada/` or change the spreadsheet or Apps Script.

Before merging, copy the server-only `application_form_secrets.py` from
`/home/aimtrave/repositories/aimtravel-testpetar/` to
`/home/aimtrave/aimtravel_site/`, preserving mode 0600. Never put its contents in
GitHub, a PR, or logs. Both environments use the same existing webhook.

Production preflight verifies the configuration and python-docx. The rsync rule
ships only the named, blank CV template under `aimtravel_site/assets/`; other
server documents retain their existing exclusions. The production smoke check
includes the new public page. No new database models or migrations are needed.

Run `python manage.py test tests.test_public_application_form` for isolated form,
CV, CSRF and mocked webhook tests. The full CI suite remains required before merge.
An end-to-end live submission creates a real Sheet entry/CV and may trigger the
existing Apps Script emails; use an agreed test identity for that check.

The form requires a real JPEG/PNG/WEBP photo on both client and server. The
existing site logo is used in the header. Django throttles repeat submissions by
email rather than shared office/Wi-Fi IP, and allows 60 seconds for the webhook.
The existing Apps Script receiver deployment was updated to version 8: its script
lock waits up to 30 seconds and spreadsheet writes are flushed before email and
before releasing the lock. A busy response keeps the form retryable with the same
submission ID. No destinations, recipients or access permissions were changed.

## Receiver access recovery and diagnostics

On 2026-11-02 the production receiver returned HTTP 403 before executing the
submission handler. Reauthorizing its existing Google account and refreshing the
same deployment to version 11 restored access. The URL, secret, recipients and
Anyone/execute-as-owner settings were preserved. A fictional live application
returned success and was found exactly once in both destination sheets.

HTTP 401/403 from the receiver now reports a service failure with a support
reference, rather than suggesting that a student's answers or photo are invalid.
Failures and completed delivery are recorded by submission ID in the application
logger and `APPLY_PRIVATE_ROOT/application-form-events.jsonl` (created mode 0600).
The log contains only timestamp, reference, operational code and upstream HTTP
status: no answers, contact details, photos, credentials or receiver URL. Normal
private-media retention/rotation should include this diagnostic file. A logging
failure never blocks delivery. Retries retain the original ID and existing
receiver deduplication.

Accepted JPEG/PNG/WebP photos are normalized to JPEG with camera orientation
applied before Word embedding. A missing CV template is a server error, not a
photo validation error. No student document is persisted by this conversion.
