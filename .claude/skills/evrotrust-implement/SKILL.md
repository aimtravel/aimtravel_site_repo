---
name: evrotrust-implement
description: Implement Evrotrust qualified e-signature (QES) signing for the tax contract in this Django site, replacing the print/sign/scan/upload loop. Use when asked to integrate Evrotrust, add e-signing, digitally sign the contract, or work on the aimtravel_site/evrotrust app.
---

# Evrotrust e-signature integration

Plan of record for replacing the manual contract-signing loop in the `taxes` app with
Evrotrust qualified electronic signatures.

## The seam

Current flow:

1. [`generate_pdf`](../../../aimtravel_site/taxes/views.py) renders `templates/taxes/contract_template.docx`
   through `docxtpl`, then re-draws it into a PDF with ReportLab.
2. The student downloads it from the button in `templates/taxes/edit_taxes.html`.
3. They print, sign, scan.
4. They upload the scan into `Taxes.signed_and_scanned_contract` (a `PrivateFileField`).

Evrotrust replaces **steps 2–4 only**. Write the returned signed PDF back into that same
`signed_and_scanned_contract` field and nothing downstream needs to change — the `_used`
flag logic in `Taxes.save()`, the admin list, the XLS export and `private_storage_permissions`
all keep working as-is. Do not add a parallel "signed document" field.

## Which Evrotrust flow to use

Two relevant flows (see <https://docs.evrotrust.com/docs/integration>):

- **Online** — `POST /document/doc-online`, for people already registered in the Evrotrust
  mobile app. Look the person up by ЕГН + country; they get a push notification and sign there.
  `Students.bg_personal_number` in `aimtravel_site/user_profile/models.py` already holds the ЕГН.
- **Offline / one-time** — `POST /document/doc-offline` (or `/document/doc-offline-refid`),
  where the signer needs no prior registration; identification happens inline and produces a
  RefID that stays valid for about a year.

Most W&T students will not have the app installed. **Implement offline as the primary path and
online as a fast path** when `POST /user-check-extended` reports the person is registered and
ready to sign. Keep manual upload as a third fallback for anyone who refuses the app.

## Prerequisites (blocking, non-code)

A commercial contract with Evrotrust is required to obtain `client_id` / `client_secret`.
Without those, only sandbox scaffolding can be built. Confirm these exist before starting.

- Auth: OAuth2 client credentials via `/authorize/gettoken`; tokens last roughly 15 days,
  so cache them rather than fetching per request.
- Sandbox API base: `https://api.sandbox.evrotrust.com/vendor/`
- Production API base: `https://v.evrotrust.com/vendor/`
- Exact request/response field names for `doc-online` / `doc-offline` are **not** on the public
  docs pages (the `/reference/*` pages 404 without a session). Take them from the onboarding
  pack Evrotrust supplies with the credentials. Do not guess field names — ask the user for
  the spec if it is not in the repo.

## Implementation steps

### 1. Extract the PDF builder

`generate_pdf` in `aimtravel_site/taxes/views.py` mixes rendering with `HttpResponse`.
Split out `build_contract_pdf(tax) -> bytes` so the download button and the signing request
share one code path. Delete the commented-out duplicate copy of `generate_pdf` that sits
immediately above the live one while you are in there.

### 2. New app: `aimtravel_site/evrotrust/`

- `client.py` — thin `requests` wrapper (`requests==2.31.0` is already a dependency; there is
  **no** Celery or Redis in this project, so do not reach for a task queue). Token caching,
  `check_user()`, `send_for_signing()`, `check_status()`, `download_signed()`. Keep Django
  imports down to `settings` so it can be exercised directly against sandbox.
- `models.py` — `SigningRequest(tax FK, transaction_id, thread_id, status, sent_at, completed_at)`.
  This is required because signing is **asynchronous**: the student may sign hours later.
- `views.py` — `start_signing(tax_id)` (login-required; builds the PDF, calls Evrotrust, creates
  the `SigningRequest`) and `callback` (`csrf_exempt`, verifies the caller, downloads the signed
  file, writes it to `tax.signed_and_scanned_contract`, saves).
- `urls.py` — mount as `path('evrotrust/', include('aimtravel_site.evrotrust.urls'))` in
  `aimtravel_site/urls.py`.
- Register the app in `INSTALLED_APPS` in `aimtravel_site/settings.py`.

### 3. Credentials

Put `client_id` / `client_secret` in `credentials.py` and reference them from `settings.py`,
mirroring how `EMAILPASSWORD` is already handled. `credentials.py` is untracked — never commit
secrets, and never paste live credentials into a transcript, commit message or PR.

### 4. Polling fallback (do not skip)

Webhooks alone are fragile — one missed callback leaves a contract stuck forever, and there is
no queue in this project to retry with. Add a management command that polls `POST /document/status`
for pending `SigningRequest` rows, and run it from cron every 10–15 minutes.

### 5. Template

Replace the download/upload block in `templates/taxes/edit_taxes.html` (the
`signed_and_scanned_contract` section) with a "Sign with Evrotrust" button plus a status
indicator driven by `SigningRequest.status`. Keep the manual upload control available as a
fallback. UI copy in this project is Bulgarian — match it.

## Constraints to respect

- **ЕГН is sensitive personal data (GDPR).** Never log it, never put it in error messages or
  exception text, and avoid storing raw callback payloads verbatim if they echo it back.
- **Fix first:** `settings.py` sets
  `PRIVATE_STORAGE_AUTH_FUNCTION = 'aimtravel_site.taxes.views.private_storage.permissions'`,
  but the real function is `private_storage_permissions`. That dotted path resolves to a
  module attribute that does not exist. It is probably dead code because files are served via
  the app's own `serve/private/file/` route, but confirm and fix before writing signed contracts
  into `private_media/`.
- Signed contracts are legal documents. Do not delete or overwrite an existing
  `signed_and_scanned_contract` without an explicit instruction.
- Build and test against **sandbox** first. Never point at the production base URL as a default.
