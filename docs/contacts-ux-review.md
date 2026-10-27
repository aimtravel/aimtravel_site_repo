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
