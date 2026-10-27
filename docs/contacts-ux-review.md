# AIM Travel: contacts redesign

## Review scope
Contact journey: first screen, direct communication, offices, directions, inquiry
form and responsive layout. References reviewed on 27 October 2026:

- AIM Travel: https://aimtravel.bg/contacts/
- Orange: https://orange.bg/kontakti/
- Happy World: https://www.happyworld.bg/kontakti/

## Findings

Orange groups office addresses, maps, contact details and consultants clearly.
This supports location choice and trust, although its large travel hero adds
scrolling before the practical details.

Happy World makes Viber, phone and the office visible immediately and offers a
short callback form. This reduces the number of decisions before contact.

AIM has a recognizable dark/red identity and useful office information. Its
contact journey spreads actions across a long introduction, icon-only social
links, repeated map sections and an inquiry form with an extra university field.
The message field is a single-line input in the existing template.

## Staging implementation

- Clear first-screen heading and a prominent panel for Viber, Instagram and phone.
- Viber: `viber://chat?number=%2B359889966583` for the supplied ordinary/unknown
  account type. It requires an installed Viber app; actual account/device opening
  needs a phone check.
- Instagram: direct app chat plus a separate profile link for desktop fallback.
- Office cards for Sofia and Varna, preserving the published addresses and phone
  numbers. Both original Google map embeds are retained. Directions buttons use
  Google's Maps directions URL format and the corresponding office address.
- Short inquiry form: name, email, optional phone and a multiline message. The
  existing `/submit-form/` endpoint, CSRF token and backend field names are kept.
- Mobile: single-column layout and a fixed three-action contact bar with 44px
  controls. Inputs have labels and autocomplete; links have keyboard focus styles.
- Existing navigation/footer retained. Page-local fixes address a footer overflow
  and sticky-header anchor offsets.

## Deployment and verification

Staging: https://testpetar.aimtravel.bg/contacts/

Only `templates/nav/contacts.html` in the testpetar app is replaced. The old staging
template is archived locally in `backup/contacts-before-20261027.html`. Production
is unchanged.

Verified Django template parsing, staging rendering, link destinations, CSRF/form
fields, native required-field validation and absence of desktop horizontal
overflow. Contact content was checked at a 390px framed viewport using the local
rendered template; its content has no horizontal overflow and mobile controls
are at least 44px high. The site's existing mobile header was retained.

No test inquiry/email was sent. Viber and Instagram app behavior needs a device
with the respective app and account. Office hours and response-time promises are
not added because they were not supplied.


## Revision requested on 27 October

The hero now shows the full AIM logo and explains online consultation,
registration and contract signing, including for people outside Bulgaria.
The office cards use a map/details layout, the supplied office email addresses,
Instagram accounts and consultant counts (Sofia 8, Varna 3). The online team
is shown separately with 3 consultants. No staff identities or response times
have been invented. Market leadership is expressed through concrete online
services rather than an unverified comparison with every other agency.

The new callback form posts to `/contact-inquiry/`. Phone is required and email
is optional. Its image CAPTCHA is verified server-side, expires after 5 minutes,
is bound to the CSRF cookie and allows one attempt. Exclusive nonce marker files
under the staging app's `tmp/contact-captcha-used` directory prevent replay
across Passenger workers. No visitor name or contact data is stored there.
Wrong or expired codes refresh without clearing the visitor's form. This is a
self-hosted visual challenge, not a third-party CAPTCHA service, and is not a
guarantee against all automated abuse. Phone and Viber remain alternatives for
visitors who cannot use the image challenge.

Deployment now includes the new web/contact_inquiry.py module and two added
routes in the existing staging web/urls.py, in addition to the template. The
staging URL file was downloaded and backed up before the minimal edit; other
staging routes were preserved. GitHub's version retains its own route names.
Production is unchanged. The legacy submit-form endpoint remains for the
separate job-offers form and is not part of this change.

Six isolated tests passed using Django's in-memory email backend: correct code,
wrong/missing/replayed/expired/tampered/cross-cookie code, CSRF, honeypot,
invalid email, mail failure and independent visitors. Live staging was checked
for successful logo/CAPTCHA loading, enabled form controls, office contacts and
absence of desktop horizontal overflow. No real inquiry/email was sent, so SMTP
delivery has not been tested end to end in this revision.

