# AIM Travel website — aimtravel.bg

**English** · [Български](README.bg.md)

The source code of https://aimtravel.bg, the website of AIM Travel (Summer Work & Travel USA and related programmes):

- **Information** — the WAT USA programme, job offers, internships, H-2B, news, prices and contacts.
- **Accounts** — after logging in, users fill in the WAT registration and the tax-refund application.
- **Application form** "Запиши се за бригада" (`/zapisvane-za-brigada/`) — a React page that issues the contract automatically and emails it to the applicant.

Every change reaches the live site the same way: a pull request to `main`, automatic checks, merge, automatic deploy. Nobody edits files on the server.

> ⚠️ **This repository is public.** Never commit passwords, keys, `credentials.py`, database dumps or anything with applicants' personal data (names, EGN, ID-card numbers, contracts).

## Contents

1. [What is where](#1-what-is-where)
2. [Backend (Django) — local setup](#2-backend-django--local-setup)
3. [Frontend (React) — local setup](#3-frontend-react--local-setup)
4. [Production — Superhosting cPanel](#4-production--superhosting-cpanel)
5. [Making a change — pull request, review, merge](#5-making-a-change--pull-request-review-merge)

---

## 1. What is where

| Path | What it is |
|---|---|
| `aimtravel_site/` | Django project: `settings.py`, `urls.py` and the apps `web`, `main_page`, `posting`, `taxes`, `user_auth`, `user_profile`, `apply` (application form) |
| `templates/` | Django templates. `templates/apply/documents/` holds the season contract template (`contract_<season>.docx`) and the blank forms sent with every contract |
| `static/` | CSS, JS and images. On the server they are collected into `public_html/static` |
| `frontend/` | The React + TypeScript + Vite app of the application form. Its build goes to `static/dist/`, which is **not** in git — CI builds it |
| `tests/` | UI smoke tests (every public page must render) and an end-to-end test of the application form |
| `requirements-production.txt` | The exact Python packages installed on production. **The only requirements file to use** |
| `deploy/production_deploy.sh`, `.cpanel.yml` | The deploy script that runs on the server |
| `.github/workflows/` | `ci.yml` (checks on every pull request) and `deploy-production.yml` (deploy on every merge to `main`) |
| `Инструкция за ползване на AIM TRAVEL USA site.pdf` / `.docx` | User manual for editing the site's content in Django admin |

Kept from the old project — **do not use or add to them**: `requirements.txt` (an old, UTF-16 encoded list), `venv/` (an old Windows virtual environment), `staticfiles/`, `media/`, `private_media/`, `aimtravel_site_repo.rar`, `.idea/`, and the tracked `__pycache__/*.pyc` files.

---

## 2. Backend (Django) — local setup

Production runs **Python 3.11**, **Django 4.1** and **MariaDB 10.11**. Locally, use Python 3.11 and MySQL 8.4.

### 2.1 Install the tools (once)

**macOS** (with [Homebrew](https://brew.sh)):

```bash
brew install python@3.11 mysql@8.4 pkgconf git
brew link --force mysql@8.4       # puts mysql and its build files where the MySQL driver finds them
brew services start mysql@8.4     # starts MySQL now and at every login
```

**Windows**:

1. **Python 3.11** (64-bit) from https://www.python.org/downloads/ — tick *"Add python.exe to PATH"*.
2. **MySQL 8.4 LTS Community Server** from https://dev.mysql.com/downloads/mysql/ (version 8.4, *Windows (x86, 64-bit), MSI Installer*) — note the `root` password you choose.
3. **Git for Windows** from https://git-scm.com/download/win.

Use **PowerShell** for the Windows commands below.

### 2.2 Get the code

```bash
git clone https://github.com/aimtravel/aimtravel_site_repo.git
cd aimtravel_site_repo
```

### 2.3 Python virtual environment

Create it **outside** the repository folder (inside it, git would show thousands of new files).

macOS:

```bash
python3.11 -m venv ~/.venvs/aimtravel
source ~/.venvs/aimtravel/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-production.txt
```

Windows (PowerShell):

```powershell
py -3.11 -m venv $HOME\.venvs\aimtravel
& $HOME\.venvs\aimtravel\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-production.txt
```

If PowerShell refuses to run `Activate.ps1`, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once and try again.

Activate the environment (the `source …` / `& …Activate.ps1` line) in every new terminal before running `python manage.py …`.

The repository still tracks old compiled `.pyc` files, so running Python marks them as changed in `git status`. Prevent that by setting `PYTHONDONTWRITEBYTECODE=1` once:

- macOS: `echo 'export PYTHONDONTWRITEBYTECODE=1' >> ~/.zshrc` and open a new terminal
- Windows: `setx PYTHONDONTWRITEBYTECODE 1` and open a new PowerShell

If `.pyc` files show up as modified anyway, undo it with `git restore -- '*.pyc'`. Never commit them.

### 2.4 Local database

Start the MySQL client as `root`:

- macOS: `mysql -u root -p` (a fresh Homebrew MySQL has no root password — just press Enter)
- Windows: `& "C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe" -u root -p` (the default install folder; adjust it if you chose another)

Then run (choose your own local password):

```sql
CREATE DATABASE aimtravel CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'aimtravel'@'localhost' IDENTIFIED BY 'choose-a-local-password';
GRANT ALL PRIVILEGES ON aimtravel.* TO 'aimtravel'@'localhost';
-- the tests create and drop their own database, test_aimtravel
GRANT ALL PRIVILEGES ON test_aimtravel.* TO 'aimtravel'@'localhost';
```

Exit with `exit`. Every developer starts from an **empty** database. **Never copy the production database** to your computer: it holds applicants' personal data.

### 2.5 `credentials.py` (local settings)

`settings.py` contains production's values; secrets and machine-specific values come from `credentials.py`, a file next to `manage.py` that is in `.gitignore`. Create it with:

```python
# Local development only. This file is in .gitignore: never commit it.
from pathlib import Path

LOCAL_DATA = Path.home() / "aimtravel-local"  # uploads and contracts, outside the repository

SECRET_KEY = "local-development-only"
DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

DB_NAME = "aimtravel"
DB_USER = "aimtravel"
DB_PASSWORD = "choose-a-local-password"   # the password from step 2.4
DB_HOST = "localhost"

EMAIL_HOST_USER = ""
EMAILPASSWORD = ""
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"  # emails are printed in the terminal

STATICFILES_DIRS = [Path(__file__).resolve().parent / "static"]
STATIC_ROOT = LOCAL_DATA / "static"
MEDIA_ROOT = LOCAL_DATA / "media"
APPLY_PRIVATE_ROOT = LOCAL_DATA / "private"
SITE_URL = "http://127.0.0.1:8000"
```

The keys `SECRET_KEY`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `EMAIL_HOST_USER` and `EMAILPASSWORD` are required. Everything else falls back to production's value, so keep the lines above — without them Django would look for `/home/aimtrave/public_html/…`. Other optional keys are described in [section 4.3](#43-server-only-files).

### 2.6 Create the tables and an admin user

```bash
python manage.py migrate
python manage.py createsuperuser      # asks for an email and a password
python manage.py runserver
```

Open http://127.0.0.1:8000/admin/ and log in.

With an empty database, **the homepage, `/wat_usa/` and `/taxes/` show an error** until some content exists. In Django admin, add one entry in each of:

- **Главна страница**: **1. Основен слайдер**, **2. Втори слайдер**, **3. Трети слайдер**, **4. Четвърти слайдер**, **5. Секция "За нас"**, **6. Секция "Call to Action"**, **7. Секция "Видеа"**, **8. Секция "Цени"**, **9. Секция "Услуги"**
- **Блог**: **Новини** (at least one news item)
- **Администрация**: **Цени**

Then http://127.0.0.1:8000/ works.

### 2.7 Tests and lint

```bash
python manage.py test tests
```

Expect `OK (expected failures=2)`: two pages are already broken on the live site (`/prices/all/`, `/services/all/`) and are marked as known failures.

The pull-request lint checks only errors that break code, and only in the Python files you changed:

```bash
pip install ruff==0.6.9
ruff check --select E9,F63,F7,F82 path/to/changed_file.py
```

### 2.8 Things to know

- **Migrations**: the models of a few older apps differ slightly from production's migration history. A plain `python manage.py makemigrations` would therefore create unwanted migrations (and stop to ask about `news.slug`). Always name the app — e.g. `python manage.py makemigrations apply` — and read the generated file before committing it.
- **Emails** are printed in the terminal (console backend).
- **Application form**: Turnstile (the anti-bot check) is off locally. Without LibreOffice (`soffice`) the contract is created as `.docx` instead of PDF — that is fine for development.
- **New Python package**: add it with an exact version (`name==x.y.z`) to `requirements-production.txt`. The deploy installs it on the server.

---

## 3. Frontend (React) — local setup

The application form page (`/zapisvane-za-brigada/`) is a React + TypeScript app in `frontend/`, built with Vite and Tailwind. Django serves the page; the app is loaded into it by [django-vite](https://github.com/MrBin99/django-vite).

### 3.1 Install

**Node.js 24 LTS** (the version CI uses):

- macOS: `brew install node@24 && brew link --force node@24` (or with [nvm](https://github.com/nvm-sh/nvm): `nvm install 24`)
- Windows: the *LTS* installer from https://nodejs.org/

Then, from the repository folder:

```bash
cd frontend
npm ci        # installs the exact versions from package-lock.json
```

### 3.2 Develop

Run two terminals:

| Terminal 1 (repository folder, venv active) | Terminal 2 (`frontend/`) |
|---|---|
| `python manage.py runserver` | `npm run dev` |

Open **http://127.0.0.1:8000/zapisvane-za-brigada/** (Django's address, not Vite's). With `DEBUG = True` the page loads the app from the Vite dev server (`http://127.0.0.1:5173`), so changes in `frontend/src/` appear immediately.

### 3.3 Build

```bash
npm run build      # type-check + build into ../static/dist
```

`static/dist/` is in `.gitignore`: **never commit build output**. CI builds the frontend for every pull request, and the deploy installs that build on the server.

To check the built version locally, add `VITE_DEV_MODE = False` to `credentials.py`, run `npm run build`, and reload the page with only `runserver` running. Remove the line to go back to development mode.

### 3.4 Scripts

| Command | Status |
|---|---|
| `npm run typecheck` | passes |
| `npm run build` | passes — this is what CI runs ("Frontend build") |
| `npm run lint` | currently fails (1 warning; no warnings allowed) — not run by CI yet |
| `npm run format:check` | currently fails (16 files not formatted with Prettier) — not run by CI yet |
| `npm test` | currently fails: there are no frontend tests yet |

Do not commit `frontend/node_modules/`; it is in `.gitignore`.

---

## 4. Production — Superhosting cPanel

### 4.1 How it is hosted

- **Superhosting.bg** shared hosting with **cPanel**. Django runs through **Passenger** ("Setup Python App"), Python 3.11; the database is MariaDB 10.11.
- The server has **no Node.js** — the frontend is built by GitHub Actions.
- There is **no staging site**: test locally, then merge.

| On the server | Path |
|---|---|
| Django app (`BASE_DIR`) | `/home/aimtrave/aimtravel_site` |
| Python virtual environment | `/home/aimtrave/virtualenv/aimtravel_site/3.11` |
| Git copy that cPanel deploys from | `/home/aimtrave/repositories/aimtravel-production` |
| Collected static files (served by the web server) | `/home/aimtrave/public_html/static` |
| Uploaded files (public) | `/home/aimtrave/public_html/media` |
| Contracts and filled-in forms (private) | `/home/aimtrave/aimtravel_site/private_media/apply` |
| Result of the last deploy | `~/deploy-state/last-deploy.txt` |
| Backups made by the last 5 deploys (code + database) | `~/deploy-backups/` |

### 4.2 What happens when a pull request is merged

The "Deploy to production" workflow (Actions tab) runs on every push to `main`. First its **tests** job runs the checks from `ci.yml` — Django check + UI smoke tests and the frontend build (Ruff runs only on pull requests). Then the **deploy** job goes through these steps; the run's summary table uses the same numbers:

1. **cPanel repo** — the server's git copy is found through the cPanel API.
2. **Frontend build** — the build made by the checks is uploaded to the server with a checksum.
3. **Pull main** — the server's git copy is updated to the merged commit.
4. **Deploy on server** — `deploy/production_deploy.sh` runs:
   backup of the code and the database → copy the code into the app → install the frontend build →
   `pip install` (only when `requirements-production.txt` changed) → `migrate` → `collectstatic` → `check` → restart.
   If any step fails, the previous code is put back automatically.
5. **Live site check** — the public pages must answer on https://aimtravel.bg.
6. **Rollback** — only if step 5 fails: the code from the backup is restored. The database is *not* rolled back.

Open the run (Actions → Deploy to production) to see the summary table. A failed step shows the reason; the collapsed group **"cPanel deploy log"** holds the server's full output. If `main` has moved on while a run was waiting, that run deploys nothing and says so — the newer commit's own run deploys it.

To deploy `main` again without a new commit: Actions → Deploy to production → **Run workflow** (branch `main`).

### 4.3 Server-only files

These files exist only on the server and are never in git:

- **`/home/aimtrave/aimtravel_site/credentials.py`** (permissions `600`)
  - Required: `SECRET_KEY`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `EMAIL_HOST_USER`, `EMAILPASSWORD`
  - `STATICFILES_DIRS` must point to the app's `static` folder (`/home/aimtrave/aimtravel_site/static`)
  - Optional for the application form: `TURNSTILE_SITE_KEY` and `TURNSTILE_SECRET_KEY` (the anti-bot check is off until both are set), `CONTRACT_EMAIL_BCC` (extra hidden copies of every contract email, e.g. `["office@aimtravel.bg"]`), `AIM_FROM_EMAIL`, `SITE_URL`, `AIM_APPFORM_FONT_PATH` (a `.ttf` font with Cyrillic for the filled-in application form PDF, if the server has none)
- **`/home/aimtrave/aimtravel_site/wat_credentials.py`** — the Google Sheets webhook for the WAT registration

To change one, edit it in cPanel **File Manager** or **Terminal**, then restart the app: `touch /home/aimtrave/aimtravel_site/tmp/restart.txt` (or the *Restart* button in **Setup Python App**).

The workflow logs in to cPanel with three repository secrets (GitHub → Settings → Secrets and variables → Actions): `CPANEL_HOST`, `CPANEL_USER`, `CPANEL_TOKEN`. The token is created in cPanel → **Security → Manage API Tokens**. To replace it: create a new token, update the secret, then delete the old token.

### 4.4 Undoing a bad change

**Normal way** — revert in GitHub: open the merged pull request → **Revert** → this opens a new pull request → merge it when the checks pass. The previous code is deployed like any other change.

Database changes (migrations) are **not** undone by a revert or a rollback. Every deploy's database backup is in `~/deploy-backups/<time>-<commit>/db.sql.gz`; restoring it overwrites newer data, so do it only deliberately.

**Emergency** (the site is broken and the revert cannot wait for the checks) — in cPanel **Terminal**:

```bash
ls ~/deploy-backups                     # pick the folder from before the bad deploy
echo /home/aimtrave/deploy-backups/FOLDER > ~/deploy-state/ROLLBACK
cd ~/repositories/aimtravel-production && bash deploy/production_deploy.sh
cat ~/deploy-state/last-deploy.txt      # should say state=rolled_back
```

Then also revert the change in GitHub — otherwise the next deploy brings it back.

### 4.5 Rules

- **Do not edit code on the server.** Every deploy overwrites `aimtravel_site/`, `templates/`, `static/` and the root files with what is in `main`.
- **No secrets or personal data in git** — the repository is public.
- **New Python packages** go into `requirements-production.txt` with an exact version.
- Before the application form is linked from the public pages, the Turnstile keys must be set in `credentials.py`.

---

## 5. Making a change — pull request, review, merge

`main` is protected (ruleset **ruleForMain**, applies to everyone including admins):

- changes reach `main` only through a pull request — direct pushes are rejected;
- three checks must pass: **Django check + UI smoke tests**, **Frontend build**, **Ruff (changed Python files)**;
- the branch must be up to date with `main` before merging;
- force pushes and deleting `main` are blocked;
- approvals are **not** required (0), but asking a teammate to review is strongly recommended.

**Merging deploys to https://aimtravel.bg straight away.** Merge only what is ready to go live.

### 5.1 Create a branch

```bash
git switch main
git pull
git switch -c feature/short-description     # or fix/…, docs/…, ci/…
```

### 5.2 Change, test, commit

```bash
python manage.py test tests                 # and npm run build if you changed frontend/
git status                                  # check what you are about to commit
git add path/to/file1 path/to/file2         # add files by name
git commit -m "Short description of the change"
```

Before committing, make sure `git status` shows none of: `credentials.py`, `static/dist/`, `node_modules/`, `.pyc` files, database dumps or documents with personal data.

### 5.3 Push and open the pull request

```bash
git push -u origin feature/short-description
```

On GitHub, click **Compare & pull request** (or Pull requests → New pull request), check that **base is `main`**, and describe:

- **what** changes and **why**;
- **how you tested it** (tests, pages you opened);
- anything that must be done on the server (e.g. a new key in `credentials.py`).

### 5.4 Checks

The three checks run automatically and show at the bottom of the pull request.

- A red ✗ → click **Details**, read the error, fix it locally, commit and `git push` again — the checks run again.
- "This branch is out-of-date with the base branch" → click **Update branch**. If there are conflicts, update locally instead: `git switch main && git pull && git switch feature/short-description && git merge main`, resolve the conflicts, commit, `git push`.

### 5.5 Review and approve

1. Author: in the pull request, **Reviewers** (right column) → choose a teammate.
2. Reviewer: open **Files changed**, comment on lines with **+**, then **Review changes** → **Comment**, **Approve** or **Request changes** → **Submit review**.
3. Author: answer or fix every comment (new commits update the pull request) and mark conversations as **Resolved**.

### 5.6 Merge and check the deploy

1. When all checks are green (and the review is done), click **Merge pull request** → **Confirm merge**.
2. Open **Actions → Deploy to production** and wait for the run: it must end with **DEPLOYED … to https://aimtravel.bg**.
3. Open the changed pages on https://aimtravel.bg.
4. Click **Delete branch** in the pull request.

If the deploy fails, its summary says at which step and whether anything was changed — see [section 4.2](#42-what-happens-when-a-pull-request-is-merged) and [4.4](#44-undoing-a-bad-change).
