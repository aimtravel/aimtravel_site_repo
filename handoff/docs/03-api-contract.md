# API контракт

Base URL: `/api/v1`. Всички отговори са JSON. Полетата са `snake_case`
(Django конвенция); `frontend/src/apply/payload.ts` прави превода.

Съобщенията за грешка са **i18n ключове, не готов текст**. Бекендът връща
`errors.egn.checksum`, а фронтендът го подава на `t()`. Причината: един
източник за българските низове, и възможност за английска версия без
да се пипа бекендът.

---

## GET /apply/config

Какво фронтендът не бива да носи в bundle-а.

```json
{
  "season": 2027,
  "turnstile_site_key": "0x4AAA…",
  "offices": [
    { "value": "varna", "label": "Офис Варна", "address": "бул. „Владислав Варненчик“ 186" },
    { "value": "sofia", "label": "Офис София", "address": "бул. „Витоша“ 19" }
  ]
}
```

Сезонът е тук, а не в bundle-а, защото се сменя на 1 юни и не искаме rebuild
на тази дата. Turnstile ключът — защото се ротира.

В обичайния случай тази заявка **не се прави**: Django подава същите данни в
`data-bootstrap` атрибута на `#apply-root`. Endpoint-ът е резервен вариант.

---

## GET /lookup/{kind}?q=…

`kind` ∈ `universities` | `cities` | `majors`

Заявка под 2 символа връща `[]` без да пипа справочника.

```json
[
  { "value": "Икономически университет — Варна",
    "label": "Икономически университет — Варна",
    "hint": "Варна" }
]
```

Подредбата не е азбучна: съвпадение в началото се показва преди съвпадение в
средата. Търсене на „варн“ трябва да върне „Варненски свободен университет“
преди „Медицински университет … — Варна“.

Throttle: `120/min` на IP. Autocomplete-ът се вика при писане, но не безкрайно.

---

## PUT /applications/draft

Автозапис на чернова. Анонимна — `draft_id` живее в `localStorage`.

```json
{ "draft_id": "9f3a…" | null, "values": { "email": "i@x.bg", "egn": "054" } }
```
→ `{ "draft_id": "9f3a…" }`

Черновата **не се валидира**: студентът може да е стигнал до „ЕГН: 054“ и това
не е грешка. Непознати ключове се изхвърлят мълчаливо.

Черновите съдържат ЕГН и се трият след 30 дни (`purge_stale_drafts`).

---

## POST /applications

Единствената точка, която издава договор.

**Хедъри**

| Хедър | Задължителен | Защо |
| --- | --- | --- |
| `X-CSRFToken` | да | Django SessionAuthentication |
| `Idempotency-Key` | силно препоръчан | Двойно кликване или retry не издава втори договор. Един ключ на сесия на формата, не на опит. |

**Тяло**

```json
{
  "email": "ivan.petrov@gmail.com",
  "first_name": "IVAN", "middle_name": "PETROV", "last_name": "DIMITROV",
  "phone": "+359888123456",
  "date_of_birth": "2005-06-14",
  "egn": "0546140012",
  "id_card_number": "123456789",
  "place_of_birth": "Варна",

  "university": "Икономически университет — Варна",
  "major": "Информатика",
  "year_of_study": "2",

  "program_option": "full_arranged",
  "season": 2027,
  "office": "varna",

  "accepts_terms": true, "declares_truth": true, "accepts_gdpr": true,
  "turnstile_token": "0.abc…"
}
```

**201 Created**

```json
{
  "application_id": "5c0e…",
  "contract_number": "AIM-VAR-2027-00042",
  "contract_pdf_url": "https://aimtravel.bg/api/v1/contracts/5c0e…/token/",
  "email_sent_to": "ivan.petrov@gmail.com"
}
```

`contract_pdf_url` е подписан и изтича след час — договорът съдържа ЕГН.

**400 Bad Request** — грешки по поле, DRF формат:

```json
{ "egn": ["errors.egn.dobMismatch"], "date_of_birth": ["errors.dateOfBirth.age"] }
```

или общо: `{ "detail": "errors.antibot.failed" }`

**429** — надхвърлен лимит. `{ "detail": "errors.tooManyRequests" }`

**503** — договорът не се генерира (LibreOffice падна, липсва темплейт).
Заявката е записана със статус `contract_failed` и номерът е зает; агентът
я пуска отново от админа.

### Правила за валидация

| Поле | Правило | Ключ при грешка |
| --- | --- | --- |
| `email` | RFC формат | `errors.email.invalid` |
| трите имена | `^[A-Za-z][A-Za-z'\-]{1,29}$`, uppercase-ват се | `errors.{field}.latin` |
| `phone` | нормализира се към `+3598[789]XXXXXXX` | `errors.phone.invalid` |
| `egn` | 10 цифри + контролна цифра по БДС | `errors.egn.checksum` |
| `egn` ↔ `date_of_birth` | датата в ЕГН-то трябва да съвпада | `errors.egn.dobMismatch` |
| `date_of_birth` | 18–28 г. **на 1 юни от сезона** | `errors.dateOfBirth.age` |
| `id_card_number` | точно 9 цифри | `errors.idCard.invalid` |
| `season` | равен на текущия предстоящ сезон | `errors.season.stale` |
| съгласията | и трите задължително `true` | `errors.consent.{terms,truth,gdpr}` |

---

## GET /contracts/{public_id}/{token}/

Сваляне на договора. Токенът е `TimestampSigner` подпис с давност един час.
Невалиден или изтекъл токен връща 404, а не 403 — не потвърждаваме, че такъв
договор съществува.
