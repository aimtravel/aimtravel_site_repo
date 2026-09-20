# Known failure modes on staging.aimtravel.bg

Each entry: **symptom** (what the user sees) → **diagnosis** (how to be sure) → **recovery** (exact commands). Ordered by how often each hit us during the initial deploy.

---

## #1 — HTTP 403 Forbidden ("Server unable to read htaccess file")

**Symptom:** browser or curl returns 403 with body "You don't have permission to access this resource. Server unable to read htaccess file, denying access to be safe." Response header `server: Apache`, no `x-powered-by: Passenger`.

**Diagnosis:**
```bash
ls -ld /home/aimtrave/staging.aimtravel.bg
ls -la /home/aimtrave/staging.aimtravel.bg/.htaccess
```
Cause is one of:
- App root is `drwx------` (700) instead of `drwxr-xr-x` (755) or `drwxr-x---` (750). Apache runs under an isolated user that needs to traverse in.
- `.htaccess` is chmod 600 (owner-only) instead of 644.

**Root cause:** running `rsync -a` (archive mode preserves source permissions). Fresh `git clone` gives directories mode 700 under a strict umask; rsyncing those over the deploy dir strips Apache's read/traverse access. **The deploy script must use `rsync -rlt`, never `-a`.**

**Recovery:**
```bash
chmod 755 /home/aimtrave/staging.aimtravel.bg
chmod 644 /home/aimtrave/staging.aimtravel.bg/.htaccess
chmod 644 /home/aimtrave/staging.aimtravel.bg/passenger_wsgi.py
find /home/aimtrave/staging.aimtravel.bg -type d -exec chmod 755 {} \;
find /home/aimtrave/staging.aimtravel.bg/staticfiles -type f -exec chmod 644 {} \;
find /home/aimtrave/staging.aimtravel.bg/static -type f -exec chmod 644 {} \;
chmod 600 /home/aimtrave/staging.aimtravel.bg/credentials.py   # keep this one 600
touch /home/aimtrave/staging.aimtravel.bg/tmp/restart.txt
```

---

## #2 — HTTP 500 "MainSlider matching query does not exist"

**Symptom:** `curl https://staging.aimtravel.bg/` returns 500 with a large body. `x-powered-by: Phusion Passenger` present. Only the homepage `/` is affected; `/zapisvane-za-brigada/` returns 200 fine.

**Diagnosis:** run this in cPanel Terminal (venv active):
```bash
python <<'PYEOF'
import os, sys, traceback
sys.path.insert(0, "/home/aimtrave/staging.aimtravel.bg")
os.environ["DJANGO_SETTINGS_MODULE"] = "aimtravel_site.settings"
import django; django.setup()
from django.test import Client
c = Client(HTTP_HOST="staging.aimtravel.bg")
try:
    resp = c.get("/")
    print("Status:", resp.status_code)
except Exception:
    traceback.print_exc()
PYEOF
```

Traceback ends in `aimtravel_site.main_page.models.MainSlider.DoesNotExist`. The homepage view at `aimtravel_site/main_page/views.py:69` calls `MainSlider.objects.latest('id')` without handling the empty case.

**This is not a deploy failure.** The staging DB is empty by design (fresh `migrate`). Do not "fix" it as part of a deploy — it needs one of:
- Application-level fix (wrap in try/except) — proper PR against the branch.
- DB seed via `createsuperuser` + manual add via `/admin/`.
- Production DB dump imported into staging.

Direct users to the feature route `/zapisvane-za-brigada/` and confirm THAT returns 200. Do not report deploy as failed.

---

## #3 — HTTP 500 on `/zapisvane-za-brigada/` (real Django exception)

**Symptom:** feature route returns 500. `x-powered-by: Phusion Passenger` present.

**Diagnosis:** repeat the test-Client block from #2, but with `resp = c.get("/zapisvane-za-brigada/")`. Read the traceback.

Common causes:
- Missing migration → `python manage.py migrate --noinput` (Phase 5 should have caught this).
- Missing Vite manifest → check `ls /home/aimtrave/staging.aimtravel.bg/staticfiles/dist/manifest.json`; if missing, re-run collectstatic.
- Missing template → check `templates/apply/zapisvane.html` exists on server.

---

## #4 — HTTP 404 with `server: Apache` (no Passenger header)

**Symptom:** feature route returns 404. `x-powered-by: Passenger` is **absent**. `content-type: text/html; charset=iso-8859-1` (Apache default, not Django).

**Diagnosis:** Passenger is not routing the request to Django at all — either the app is stopped or `.htaccess` was destroyed.

```bash
ls -la /home/aimtrave/staging.aimtravel.bg/.htaccess
cat /home/aimtrave/staging.aimtravel.bg/.htaccess
ls -la /home/aimtrave/staging.aimtravel.bg/passenger_wsgi.py
```

If `.htaccess` or `passenger_wsgi.py` is missing → cPanel destroyed the Python App. Follow **#6**.

If both exist and look right → open cPanel → Setup Python App → check the app status. If Stopped, click Start. If Running, click Restart (through UI, more reliable than `touch tmp/restart.txt` when things are unstable).

---

## #5 — HTTP 500 with `ModuleNotFoundError: No module named 'pkg_resources'`

**Symptom:** Django refuses to start; traceback ends at `from pkg_resources import DistributionNotFound, get_distribution` inside `model_utils/__init__.py`.

**Diagnosis:** `pip show setuptools` shows version >= 81. Setuptools 81 removed `pkg_resources`; `django-model-utils` 4.3.x still imports it.

**Recovery** — upgrade `django-model-utils` past the pkg_resources dep:
```bash
pip install --upgrade "django-model-utils>=5.0"
python manage.py check
```

---

## #6 — cPanel says "No such application (or application not configured) 'staging.aimtravel.bg'"

**Symptom:** cPanel → Setup Python App shows the error banner and a "CREATE APPLICATION" button. `.htaccess` and `passenger_wsgi.py` are missing from the app root. All other files (aimtravel_site/, static/, etc.) are still there. Site returns 404 with `server: Apache`.

**Diagnosis:** the Python App registration was destroyed. Likely trigger: user hit "Destroy" or an equivalent in cPanel, or dopushed a "delete app" action while trying to restart.

**⚠️ CRITICAL: the venv at `/home/aimtrave/virtualenv/staging.aimtravel.bg/3.11/` is likely gone too.** Even if the shell prompt still shows `(staging.aimtravel.bg:3.11)`, `pip list` may return only pip/setuptools. Confirm before assuming packages are intact:
```bash
source /home/aimtrave/virtualenv/staging.aimtravel.bg/3.11/bin/activate
pip show django 2>&1 | head -3
```
If Django is not shown → venv was reset; you will also need to run failure #7's reinstall block.

**Recovery:**

**Step 1 — recreate the app in cPanel UI (not from terminal):**
- cPanel → Setup Python App → CREATE APPLICATION
- Python version: `3.11`
- Application root: `staging.aimtravel.bg`
- Application URL: domain `staging.aimtravel.bg`, path empty
- Application startup file: `passenger_wsgi.py`
- Application Entry point: `application`
- Do NOT tick any "wipe directory" / "reset virtualenv" option.

This regenerates `.htaccess` and a placeholder `passenger_wsgi.py`, and creates `tmp/` and `public/`.

**Step 2 — restore server-managed files** using the templates in [file-templates.md](file-templates.md): credentials.py, aimtravel_site/__init__.py, settings.py patches, passenger_wsgi.py.

**Step 3 — if pip show django failed above, reinstall packages** using failure #7's block.

**Step 4 — verify + restart:**
```bash
python manage.py check
touch tmp/restart.txt
```

Then curl from Mac.

---

## #7 — `ModuleNotFoundError: No module named 'django'` after cPanel actions

**Symptom:** `python manage.py check` returns `ModuleNotFoundError: No module named 'django'`. Yet the shell prompt shows `(staging.aimtravel.bg:3.11)` and `which python` points to the venv.

**Diagnosis:** cPanel recreated an empty virtualenv at the same path. `pip list` will show only pip + setuptools (+ maybe wheel).

**Recovery — full reinstall using the corrected strip list:**
```bash
cd /home/aimtrave/staging.aimtravel.bg
source /home/aimtrave/virtualenv/staging.aimtravel.bg/3.11/bin/activate

# Ensure requirements.txt is UTF-8 (git checkout brings it back as UTF-16)
if file requirements.txt | grep -q UTF-16; then
    iconv -f UTF-16 -t UTF-8 requirements.txt | tr -d '\r' > requirements.txt.utf8
    mv requirements.txt.utf8 requirements.txt
fi

# Strip 30+ bogus / wrong-OS / wrong-DB / wrong-framework / cairo-stack pins
sed -i.bak -E '/^(docs|gnu|gulp|psycopg2|PyGetWindow|windows-curses|virtualenvwrapper-win|PyAutoGUI|MouseInfo|PyMsgBox|PyScreeze|PyRect|pytweening|pyperclip|Flask|Flask-SQLAlchemy|SQLAlchemy|mysqlclient|weasyprint|pycairo|pydyf|pyphen|rlPyCairo|svglib|xhtml2pdf|pyHanko|pyhanko-certvalidator|pdfreader|PyPDF2|pdfkit|docxcompose)==/d' requirements.txt

pip install --upgrade pip "setuptools<81" wheel
pip install -r requirements.txt
pip install -r requirements-apply.txt
pip install whitenoise "django-model-utils>=5.0"

python -c "import django, pymysql, whitenoise, rest_framework, django_vite; print('Django', django.get_version(), 'OK')"
python manage.py check
```

Why `setuptools<81`: newer setuptools removed `pkg_resources` — see failure #5. Even with upgraded `django-model-utils`, pinning `<81` avoids surprises from transitive deps.

---

## #8 — `Building wheel for mysqlclient (pyproject.toml) ... error` / `Permission denied: 'gcc'`

**Symptom:** `pip install -r requirements.txt` fails building `mysqlclient` with `Permission denied: 'gcc'` or `Permission denied: 'meson'`.

**Diagnosis:** Superhosting shared plan blocks native compilers. Any package with C extensions can't build from source.

**Recovery:** the strip list in failure #7 already removes `mysqlclient`, `pycairo`, `weasyprint`, and their transitive pullers (`svglib`, `xhtml2pdf`). PyMySQL (pure Python, already in requirements) covers MySQL via the shim in `aimtravel_site/__init__.py`:
```python
import pymysql
pymysql.install_as_MySQLdb()
```
Django's `django.db.backends.mysql` backend uses PyMySQL transparently — no settings.py change.

---

## #9 — `git status` on Mac shows thousands of untracked/deleted files after a cleanup

**Symptom:** VSCode Source Control panel shows 7000+ changed files. Files like `.gitignore`, `README.md`, `pyproject.toml`, `venv/` show as deleted (D). Files under `.idea/`, `.venv/`, `__pycache__/` show as untracked (??).

**Diagnosis:** a cleanup command intended for the server (`rm -f ...`, `rm -rf venv/`, etc.) was executed in the local Mac terminal instead of cPanel Terminal. Since `.gitignore` was among the deleted files, all previously-ignored directories now appear untracked.

**Recovery:**
```bash
cd /Users/sstoy2/aimtravel_site_repo
git restore .
git status --short | wc -l   # should print 0 or close to it
```

This restores all deleted tracked files (including `.gitignore`) from HEAD. Local uncommitted edits to tracked files WOULD be lost — check with `git diff` first if you are unsure whether the user had unsaved work.

**Prevention:** never paste a command intended for the server into the local terminal. Always prefix a server command with a comment like `# RUN IN cPanel TERMINAL ON SERVER` when passing it to the user.

---

## #10 — `curl: /bin/curl: Permission denied` in cPanel Terminal

**Symptom:** running `curl` inside cPanel Terminal returns `Permission denied`.

**Diagnosis:** Superhosting blocks outbound HTTP from shared accounts (anti-abuse). This is not fixable server-side.

**Recovery:** run all HTTP validation from the Mac's local terminal, not from cPanel Terminal.

---

## Header decoder — read this first when a request fails

| Response header contains | Passenger involved? | Where to look |
|---|---|---|
| `server: Apache` + `x-powered-by: Phusion Passenger` | yes → routed to Django | Django-level bug → failure #2 or #3 |
| `server: Apache` (no x-powered-by) | no → Apache handled directly | .htaccess/Passenger config missing → failure #4 or #6 |
| `content-type: text/html; charset=iso-8859-1` | usually no | Apache default response, not Django |
| `content-type: text/html; charset=utf-8` | usually yes | Django rendered a response (200 or 500 template) |
