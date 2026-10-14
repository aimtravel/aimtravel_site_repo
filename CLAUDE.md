# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Django 4.1 site for https://aimtravel.bg (AIM Travel, Work & Travel USA) plus one React page, the application form at `/zapisvane-za-brigada/`. `README.md` / `README.bg.md` are the full developer guide (local setup on macOS/Windows, production layout, PR workflow).

## Ground rules

- **The repository is public.** Never commit `credentials.py`, `wat_credentials.py`, DB dumps, or anything with applicants' personal data (EGN, ID-card numbers, contracts). `media/contracts` and similar contain test data only.
- **Merging to `main` deploys to production immediately** (no staging). `main` is protected: PR-only, required checks *Django check + UI smoke tests*, *Frontend build*, *Ruff (changed Python files)*, branch must be up to date.
- Production code on the server is overwritten by every deploy — never suggest editing files on the server; every change goes through a PR.
- Legacy, do not use or extend: `requirements.txt` (old, UTF-16), `venv/`, `staticfiles/`, `media/`, `private_media/`, `aimtravel_site_repo.rar`, `.idea/`, tracked `__pycache__/*.pyc`, and `aimtravel_site/templates/` + `aimtravel_site/manage.py` / `requirements.txt` (stale copies — the live templates are in the top-level `templates/`).
- Many docstrings/comments (especially in `aimtravel_site/apply/`) are in Bulgarian; UI text is Bulgarian.

## Commands

Python 3.11, MySQL (production is MariaDB 10.11; locally MySQL 8.4). Set `PYTHONDONTWRITEBYTECODE=1` — the repo still tracks `.pyc` files, and running Python otherwise dirties `git status` (undo with `git restore -- '*.pyc'`).

```bash
pip install -r requirements-production.txt        # the ONLY requirements file; new packages go here pinned (name==x.y.z)
python manage.py check
python manage.py runserver
python manage.py test tests                          # expect "OK (expected failures=2)"
python manage.py test tests.test_apply_form.ApplicationFormTest.test_page_renders   # single test
python manage.py makemigrations <app_label>          # ALWAYS name the app (see Migrations)

# CI lint: only code-breaking errors, only on changed files
ruff check --select E9,F63,F7,F82 path/to/changed_file.py   # ruff==0.6.9
```

Frontend (`frontend/`, Node 24):

```bash
npm ci
npm run dev          # Vite on 127.0.0.1:5173; open the page via Django (127.0.0.1:8000/zapisvane-za-brigada/)
npm run build        # tsc -b + vite build → ../static/dist (gitignored; this is what CI runs)
npm run typecheck
```
`npm run lint`, `format:check` and `npm test` currently fail (1 lint warning, unformatted files, no tests) and are not run by CI.

## Configuration: `credentials.py`

`aimtravel_site/settings.py` is production's settings file and does `import credentials` (a gitignored file next to `manage.py`). Required keys: `SECRET_KEY`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `EMAIL_HOST_USER`, `EMAILPASSWORD`. Everything else is read with `getattr(credentials, ..., <production default>)` — so a local file must override `DEBUG`, `ALLOWED_HOSTS`, `STATICFILES_DIRS`, `STATIC_ROOT`, `MEDIA_ROOT`, `APPLY_PRIVATE_ROOT`, `SITE_URL`, `EMAIL_BACKEND`, or Django points at `/home/aimtrave/public_html/...`. Optional: `VITE_DEV_MODE`, `TURNSTILE_SITE_KEY`/`TURNSTILE_SECRET_KEY` (Turnstile is disabled unless both set), `CONTRACT_EMAIL_BCC`, `AIM_FROM_EMAIL`, `AIM_APPFORM_FONT_PATH`, `DB_HOST`/`DB_PORT`. See README §2.5 for a template; CI writes its own throwaway one in `.github/workflows/ci.yml`.

When adding a setting, follow the same pattern: secrets come only from `credentials.py`; environment-specific values use `getattr` with production's value as default.

## Architecture

- **Project package** `aimtravel_site/` (settings, root `urls.py`, `wsgi.py`; `passenger_wsgi.py` at repo root is the cPanel/Passenger entry point). `TEMPLATES.DIRS` is the top-level `templates/`. Custom user model: `user_auth.AppUser` (email login).
- **Django apps** (`aimtravel_site.<app>`): `web` (largest — offers/job offers, prices, services, employers, favorites, WAT 2027 registration that posts to a Google Sheets webhook configured via `wat_credentials.py`/env; also the 404/500 handlers), `main_page` (homepage slider/section models — views call `.latest()` on them), `posting` (news with CKEditor 5), `taxes` (tax-refund applications, document uploads), `user_auth`, `user_profile`, `apply`.
- **Empty DB gotcha:** the homepage, `/wat_usa/` and `/taxes/` 500 until admin content exists (one record of each `main_page` section model, a `News`, a `Prices`). The smoke tests handle this by seeding one generic placeholder row per model (`tests/test_ui_smoke.py`, `SeededTestCase`).
- **Tests** live only in top-level `tests/` (per-app `tests.py` files are empty stubs): `test_ui_smoke.py` asserts every public page renders 200 with an "AIM Travel" `<title>`; pages already broken in production (`/prices/all/`, `/services/all/`) are `expectedFailure`, so fixing them surfaces as an unexpected pass. `test_apply_form.py` is the end-to-end test of the application form.

### Application form (`apply` app + `frontend/`)

- Django serves the HTML shell (`apply/pages.py`, never-cached, bootstraps CSRF + season) and loads the React bundle via **django-vite** (`DJANGO_VITE` in settings: dev server when `VITE_DEV_MODE`, else `static/dist/manifest.json`). React entry: `frontend/src/entries/apply.tsx`; shadcn/ui components, react-hook-form + zod, i18next (Bulgarian locales).
- JSON API under `/api/v1/` (DRF, `apply/urls.py`): `applications` (submit, idempotency key), `applications/draft` (autosave), `lookup/<kind>` (cities/majors/universities from `apply/data/`), `apply/config`, and signed contract download. Throttle scopes are in `REST_FRAMEWORK` settings (relaxed when `DEBUG`).
- Submission flow lives in `apply/services.py`, in a deliberate order: reserve contract number + save application in one transaction → render contract outside the transaction (`contracts.py`: `templates/apply/documents/contract_<season>.docx` via docxtpl → PDF with LibreOffice `soffice`, falls back to `.docx` if absent) and the filled application-form PDF (`application_form.py`, reportlab overlay merged onto the original PDF with pypdf; needs a Cyrillic TTF) → email last (`emails.py`, to applicant + BCC to the chosen office from `AIM_OFFICE_AGENTS` + `CONTRACT_EMAIL_BCC`). `tasks.py` runs "tasks" synchronously (no Celery in production).
- Contracts contain personal data, so they are stored under `APPLY_PRIVATE_ROOT` (outside the public `MEDIA_ROOT`) and served only through time-limited signed tokens (`storage.py`).
- `static/dist/` is never committed; CI builds it (the server has no Node.js).

## Migrations

Older apps' models have drifted slightly from production's migration history (e.g. `news.slug`, `working_year`, `amount_of_discount`), so a bare `makemigrations` generates unwanted migrations and stops at an interactive prompt about `news.slug`. Always run `makemigrations <app_label>` (add `--noinput` in automation) and read the generated file. Migrations are not undone by a revert or a deploy rollback.

## CI and deploy

- `.github/workflows/ci.yml` — on PRs to `main` (and reused by deploy): `manage.py check` + `manage.py test tests` against MySQL 8.0 with production's exact packages; frontend `npm ci && npm run build` (artifact `frontend-dist`); Ruff on changed `.py` files only.
- `.github/workflows/deploy-production.yml` — on push to `main`: reruns CI, then via the cPanel UAPI (secrets `CPANEL_HOST/USER/TOKEN`) uploads the frontend build with a checksum, updates the server's cPanel git repo, triggers `.cpanel.yml` → `deploy/production_deploy.sh`, then smoke-checks live pages and rolls code back on failure. A run whose commit `main` has moved past deploys nothing.
- `deploy/production_deploy.sh` (runs on the server as the cPanel user): backup code + DB (last 5 in `~/deploy-backups`) → rsync code into `/home/aimtrave/aimtravel_site` with `--delete` and excludes (`media/`, `private_media/`, `*credentials*.py`, `settings?*.py`, `*.zip`/`*.rar`, …) → install frontend build → `pip install` only if `requirements-production.txt` changed → `migrate` → `collectstatic` (from `static/` into `public_html/static`) → `check` → restart (`tmp/restart.txt`); self-restores on any failure. Result in `~/deploy-state/last-deploy.txt`.
- Anything that needs a server-side change (new `credentials.py` key, etc.) must be called out in the PR description.
