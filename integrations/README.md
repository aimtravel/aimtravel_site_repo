# Online registrations

`online_registration.gs` extends the existing private Application Form Apps Script.
In `doPost`, immediately after its existing secret check and inside its existing
ScriptLock, dispatch `body.action === 'online_registration'` to
`upsertOnlineRegistration_(body)`. Preserve the original CV submission flow.
Publish a new version of the existing deployment; do not change its URL or access.

The dedicated “Записани онлайн” sheet uses columns A:S for the export and T for
staff notes. UUID in S identifies the row. The receiver also accepts the previous
layout with a base-fee column during rollout, without changing the server payload.
All writes run under the receiver's
ScriptLock, and repeat delivery updates the existing row. Staff notes are preserved.
Amounts are numeric; untrusted text is escaped to prevent spreadsheet formulas.
EGN, ID card numbers and signed document download links are not exported.

The application reuses server-only `application_form_secrets.py`. Each completed
registration exports after both email attempts, independently of email success.
Failures remain visible in Django admin and can be retried with its sheet action.
Install a five-minute server cron (use the existing production Python environment):

```sh
*/5 * * * * /usr/bin/flock -n /home/aimtrave/deploy-state/online-registration-sync.lock /bin/sh -c 'cd /home/aimtrave/aimtravel_site && /home/aimtrave/virtualenv/aimtravel_site/3.11/bin/python manage.py sync_online_registrations --limit 100' >/dev/null 2>&1
```

`manage.py sync_online_registrations --all --limit 1000` backfills EUR registrations
without sending emails. Repeating it is safe. Legacy USD registrations are excluded.
Test the receiver logic with `node integrations/test_online_registration.cjs`.
