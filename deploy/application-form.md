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
