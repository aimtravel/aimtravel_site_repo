# 08 — Evrotrust e-Signing Integration Plan

**Goal:** let students sign their Work & Travel contract electronically with Evrotrust, with a qualified electronic signature (QES) that is legally equal to a handwritten one. The current "download, sign by hand, send a scan" flow stays as a fallback.

**Approach:**
- **Phase 1:** In-App signing. The student signs in the free Evrotrust mobile app.
- **Phase 2:** No-app signing. The student verifies their identity in the browser and signs with an SMS code.

---

## At a glance

| Phase | What | Blocks the next phase? |
|---|---|---|
| 0 | Business, legal and account setup | Yes. There are no credentials without it. |
| 1 | Codebase fixes that must come first | Yes. Signed contracts must not be stored publicly. |
| 2 | Evrotrust client and data model | Yes |
| 3 | Signing flow: backend, callback, polling | Yes |
| 4 | Frontend, emails, admin | No |
| 5 | Sandbox testing, then production go-live | Needed before launch |
| 6 | No-app signing (browser identity check + SMS code) | Optional, later |

---

## Phase 0 — Business & account setup (no code)

- [ ] **0.1 Sign the commercial contract with Evrotrust.** This creates our vendor account. Agree the price per signature and ask whether rejected or expired requests are billed.
- [ ] **0.2 Choose the signature level.** QES is recommended for contracts. Confirm with our lawyer.
- [ ] **0.3 Decide how AIM signs.** Options: the manager's personal QES, a company seal, or automated company signing. Also decide the order (student first, then AIM).
- [ ] **0.4 Get sandbox access.** We need `vendorNumber`, the API key, a sandbox build of the Evrotrust app, and test users.
- [ ] **0.5 Send onboarding details to Evrotrust.** These are the callback URLs (staging and production) and our logo (195×40 px, JPG). Ask whether they need to allow our server IPs.
- [ ] **0.6 Update the GDPR texts.** The EGN (Bulgarian personal number), phone and email will go to Evrotrust. Update the privacy notice and the consent text, and check the data processing agreement.
- [ ] **0.7 Agree the scope for edge cases.** Two cases need a decision:
  - Students under 18. Evrotrust returns error `479` for age.
  - Students without a Bulgarian ID.

### Questions for Evrotrust (not answered in the public docs)

- [ ] How do we verify that a callback really comes from Evrotrust? What is the retry policy, and which IPs send callbacks?
- [ ] What format does the signed file come in: a PDF with the signature embedded (PAdES) or a separate signature file?
- [ ] What is the maximum file size, and which file types are accepted?
- [ ] How do we control where the signature appears on the page: `annotationParameters` or `coverage`?
- [ ] Can the contract and the application form be sent as one group (the `/document/group/online` endpoint)?
- [ ] What are the valid `certificateType` values, and which fields are required in `users[]`?

---

## Phase 1 — Codebase fixes that must come first

- [ ] **1.1 Move contracts to private storage.** Today they sit in public `MEDIA_ROOT/contracts/` under guessable names ([settings.py:185](../../aimtravel_site/settings.py)). Store them under `private_media` and serve them only through the token-protected download view.
- [ ] **1.2 Stop the signing flow when there is no PDF.** `render_contract()` falls back to a .docx when `soffice` is missing. Signing must fail loudly instead.
- [ ] **1.3 Email the student, not the office.** Change `to=[settings.AIM_CONTRACT_EMAIL_TO]` to `application.email` in `apply/emails.py`, and keep the office in CC or BCC.
- [ ] **1.4 Normalise phone numbers** to the international E.164 format (`+359…`) when the application is saved.
- [ ] **1.5 Check the EGN.** It is optional today but is the best identifier for Evrotrust. Validate the checksum when it is present.
- [ ] **1.6 Set the real `SITE_URL`** on staging and production so that callback URLs are public and use HTTPS.

---

## Phase 2 — Evrotrust client & data model

- [ ] **2.1 Add settings.** Add `EVROTRUST_BASE_URL`, `EVROTRUST_VENDOR_NUMBER`, `EVROTRUST_API_KEY` and `EVROTRUST_CALLBACK_SECRET`. Read them from `credentials.py` with `getattr(credentials, …)` and never commit them.
  - Sandbox URL: `https://api.sandbox.evrotrust.com/vendor/`
  - Production URL: `https://v.evrotrust.com/vendor/`
- [ ] **2.2 Build the API client** in a new `apply/evrotrust.py`:
  - `_auth_header(body)` computes `hex(HMAC-SHA256(key=SHA256(api_key), msg=body))`.
  - `user_check(egn|phone|email)` calls `/user/check`. A 204 means the student has an account; a 438 means they don't.
  - `send_document(pdf, signers, expires, callback_url)` calls `/document/doc/online` and returns the `transactionID`.
  - `get_status(transaction_id)` calls `/document/status`.
  - `download(transaction_id)` calls `/document/download` and returns the signed file bytes.
  - `withdraw(transaction_id)` calls `/document/withdraw`.
- [ ] **2.3 Unit-test the client.** Cover the HMAC header against the example in the docs and mock every HTTP response code.
- [ ] **2.4 Add a `SignatureRequest` model** linked to `Application`. Fields:
  - `transaction_id`, `thread_id`, `status`, `reject_reason`
  - `sent_at`, `signed_at`, `expires_at`
  - `signed_pdf` (private storage)
  - `callback_log` (JSON)
- [ ] **2.5 Map Evrotrust status codes** to a choices enum:

  | Code | Meaning |
  |---|---|
  | 1 | Pending |
  | 2 | Signed |
  | 3 | Rejected |
  | 4 | Expired |
  | 5 | Failed |
  | 6 | Withdrawn |
  | 7 | Undeliverable |
  | 8 | Failed face recognition |
  | 99 | On hold |

- [ ] **2.6 Write the migration.**

---

## Phase 3 — Signing flow (backend)

- [ ] **3.1 Signing endpoint.** `POST api/v1/applications/<public_id>/<token>/sign`, which reuses the signed token from the download link. It:
  1. Runs `user_check`.
  2. If the student has an account, sends the contract, creates the `SignatureRequest` and returns `pending`.
  3. If not (438), returns `no_account` plus install instructions and does not send anything.
- [ ] **3.2 Callback endpoint.** `POST api/v1/evrotrust/callback/<EVROTRUST_CALLBACK_SECRET>/` (CSRF-exempt). It:
  1. Records the payload.
  2. Re-checks the status with `get_status()` rather than trusting the payload.
  3. If the contract is signed, downloads it, saves it privately and triggers the "signed" email.
  4. Always replies `204`.
- [ ] **3.3 Make the callback idempotent.** A repeated callback for an already-final request must do nothing.
- [ ] **3.4 Polling fallback.** Add a management command `poll_evrotrust_signatures` that re-checks requests that are pending and older than 15 minutes, and marks expired ones. Schedule it with cPanel cron.
- [ ] **3.5 Log API errors** with the contract number, and never log the EGN.

---

## Phase 4 — Frontend, emails, admin

- [ ] **4.1 "Sign with Evrotrust" button** next to Download in [ContractIssued.tsx](../../frontend/src/apply/ContractIssued.tsx). Add the API call and types in [api.ts](../../frontend/src/api/api.ts).
- [ ] **4.2 Three UI states:**
  - `pending`: "Open the Evrotrust app to sign."
  - `no_account`: install the app, register, then retry. Offer the manual option.
  - `signed`: success.
- [ ] **4.3 Contract email:** add the signing link to "Следващи стъпки" (next steps) in `templates/email/contract_issued.{html,txt}`.
- [ ] **4.4 New "Contract signed" email** with the signed PDF attached, sent to the student with the office in CC.
- [ ] **4.5 Admin changes:**
  - A signature status column and filter.
  - Actions to resend the signing request and to withdraw it.
  - A link to download the signed PDF.
- [ ] **4.6 Remove the stale `"photo"` step** from the step list in `ContractIssued.tsx`. It was already removed from the email.

---

## Phase 5 — Testing & go-live

- [ ] **5.1 Sandbox test on staging.** Run each case end to end:
  - The student signs.
  - The student rejects.
  - The request expires.
  - The student has no account.
  - The callback is lost (the poll command catches it).
- [ ] **5.2 Verify the signed PDF** in Adobe Reader. Optionally check it with pyHanko, which is already in `requirements.txt`.
- [ ] **5.3 Security review.** Check the callback secret, private storage, logs free of EGNs, and rate limiting on the sign endpoint.
- [ ] **5.4 Switch to production credentials.** Deploy with the `redeploy-staging` flow and adapt it for production.
- [ ] **5.5 Soft launch.** Enable signing for one office or season first, then roll it out to everyone.

---

## Phase 6 — No-app signing (later)

For students without the Evrotrust app. They verify their identity in the browser, then sign with an SMS code.

- [ ] **6.1 Request extra credentials** from Evrotrust: `client_id`, `client_secret` and the RSA-4096 public key for their browser identity check (Web SDK).
- [ ] **6.2 Get an access token** via `/authorize/gettoken` (scope `websdk`). It is valid for 15 days, so cache it.
- [ ] **6.3 Start the identity check.** Redirect the student to the Web SDK page with the encrypted `enc-data`: EGN, country, redirect URL and our reference.
- [ ] **6.4 Handle the return.** Validate the reference ID with `/onetimeidentification/validaterefid` and fetch the identity data if we need it.
- [ ] **6.5 Send the contract for signing** with `/document/doc/offline/refid`, then `/document/doc/offline/activate` with the SMS code. This must happen **within 2 hours** of the identity check.
- [ ] **6.6 Reuse the Phase 3 code** for status, callback, download and storage.

---

## References

- [Evrotrust docs index](https://docs.evrotrust.com/llms.txt)
- [Integration overview](https://docs.evrotrust.com/docs/integration)
- [Signing workflows](https://docs.evrotrust.com/docs/integration-options.md)
- [Signature types & levels](https://docs.evrotrust.com/docs/signature-types.md)
- [Authorisation (HMAC)](https://docs.evrotrust.com/reference/authentication-1.md)
- [User check](https://docs.evrotrust.com/reference/checkuservendor.md)
- [Send file (online)](https://docs.evrotrust.com/reference/post_document-doc-online.md)
- [Document ready callback](https://docs.evrotrust.com/reference/readydocument.md)
- [Download signed file](https://docs.evrotrust.com/reference/post_document-download.md)
- [One-time signatures](https://docs.evrotrust.com/reference/signing-without-integration.md)
