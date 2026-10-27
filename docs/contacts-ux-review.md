# AIM Travel contacts redesign

Staging: https://testpetar.aimtravel.bg/contacts/
Branch: codex/staging-contacts-redesign

## Final layout

Offices are the primary content. A compact page heading and anchor navigation
lead directly to Sofia and Varna. Each office has a large map, structured address,
visible phone numbers, email links, directions and a separate team summary.
The visual hierarchy follows the supplied Orange contact-page reference while
using AIM branding, existing maps and the site's Sofia Sans typeface.

Sofia: 088 996 6583 and 088 478 3801; studentski@aimtravel.bg and
sofia@aimtravel.bg; 8 office consultants.
Varna: 0878 630 072; varna@aimtravel.bg; 3 office consultants.

Each office has its own Instagram follow link with the Instagram icon, separated
from consultant information by spacing and a divider. Shared Facebook and TikTok
profiles appear in a separate general social section. The user confirmed the
TikTok destination as https://www.tiktok.com/@aimtravel_usa.
No duplicate hero logo, invented staff profiles or unsupported office hours.

Online consultation, registration and contracts remain prominent in their own
section, reachable directly from the top navigation. Copy presents online
service as an available option alongside the offices. It no longer claims
that the agency works predominantly online. The online team has 3 consultants.

Mobile layout places contact details before each map. Primary phone buttons are
at least 44px tall, text fields use 16px type, focus indicators are visible and
anchor destinations account for the fixed site navigation.

## Form and delivery

The callback form and submission JavaScript were preserved unchanged during
this visual refactor. The server verifies its one-attempt, five-minute image
CAPTCHA, CSRF binding and honeypot. Nonce files prevent reuse across workers.
The contact endpoint remains /contact-inquiry/.

Staging had no SMTP password. The contact endpoint therefore uses the hosting
account's local /usr/sbin/sendmail transport with studentski@aimtravel.bg as
sender and recipient. Configured SMTP continues to be used when credentials
are available. SMTP failures never cause a second delivery attempt through the
local transport. The user approved one test email and confirmed receipt.
Eight isolated backend tests passed after that repair.

## Validation and deployment

The revised Django template parsed successfully. The form and submission script
were compared against the previous deployed revision and match exactly.
Live staging checks confirmed both office cards, all phone/email destinations,
Instagram profile URLs, anchor navigation and CAPTCHA image loading.
No desktop horizontal overflow at 870px and 1280px browser widths.
The rendered contact component was checked at framed 390px and 320px mobile
widths without horizontal overflow. The existing mobile site navigation is
outside the isolated preview's scope.

Only the contact template changed in this visual refactor. It was uploaded to
the testpetar app and that app was restarted. Production was not deployed.
The previous template is backed up in backup/contacts-before-office-refactor.html.

## Direct-contact refinement

The page now opens with three prominent actions: Viber, free consultation and
phone call. The mobile action bar contains the same three destinations. Online
services use the same neutral navigation color as the other sections, and the
online panel has a neutral border. Sofia email is lowercase in both label and
mailto destination. The backend and form submission behavior were not changed.
Live staging verification checked all three destinations and no desktop overflow.

