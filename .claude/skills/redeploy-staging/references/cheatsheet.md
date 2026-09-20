# Redeploy cheatsheet

Sequential command list for the manual deploy path. Copy-paste each block in the order below. Fill in `<BRANCH>` with the current branch name (usually `feature/implement-new-application-form`).

Assumes: previous deploy worked and the environment is intact (venv alive, `.htaccess` present, `passenger_wsgi.py`, `credentials.py` and `aimtravel_site/__init__.py` all in place). If the site is broken before you start — see [known-failures.md](known-failures.md) first.

---

## 1. Local preflight (Mac terminal)

```bash
cd /Users/sstoy2/aimtravel_site_repo
git status --short
git log -1 --oneline
git rev-parse --abbrev-ref HEAD
```

Working tree must be clean OR every edit intended for this deploy must be committed. If the branch is ahead of origin, push it:

```bash
git push origin <BRANCH>
```

---

## 2. Local frontend build (Mac, ONLY if `frontend/src/` changed)

```bash
cd /Users/sstoy2/aimtravel_site_repo/frontend
./node_modules/.bin/vite build
```

`./node_modules/.bin/vite build` — not `npm run build`. The latter runs `tsc -b` first, which fails on a known TypeScript bug in `DateOfBirthPicker.tsx`; the produced runtime code is identical.

Commit the built bundle so the server picks it up via rsync (much simpler than the zip/upload dance):

```bash
cd /Users/sstoy2/aimtravel_site_repo
git add static/dist/manifest.json 'static/dist/assets/apply-*'
git commit -m "chore(frontend): rebuild apply bundle"
git push origin <BRANCH>
```

---

## 3. Server pull + rsync (cPanel Terminal)

Paste as one block:

```bash
source /home/aimtrave/virtualenv/staging.aimtravel.bg/3.11/bin/activate && cd /home/aimtrave/staging.aimtravel.bg

cd /home/aimtrave/repos/aimtravel-site && git pull

rsync -rlt \
  --exclude='.git' \
  --exclude='.claude' --exclude='.idea' --exclude='.vscode' \
  --exclude='.venv/' --exclude='venv/' \
  --exclude='__pycache__/' --exclude='__MACOSX/' --exclude='.DS_Store' \
  --exclude='node_modules/' \
  --exclude='credentials.py' \
  --exclude='aimtravel_site/__init__.py' \
  --exclude='aimtravel_site/settings.py' \
  --exclude='passenger_wsgi.py' \
  --exclude='*.rar' --exclude='handoff/' --exclude='prototype/' \
  --exclude='*.docx' --exclude='*.pdf' \
  --exclude='staticfiles/' --exclude='media/' --exclude='private_media/' \
  --exclude='.htaccess' --exclude='tmp/' --exclude='public/' --exclude='cgi-bin/' \
  --exclude='.well-known/' --exclude='README.md' --exclude='.gitignore' \
  --exclude='pyproject.toml' \
  /home/aimtrave/repos/aimtravel-site/ /home/aimtrave/staging.aimtravel.bg/
```

`rsync -rlt` — not `-a`. Archive mode preserves source permissions and re-breaks Apache's read on `.htaccess` and the app root (403 loop).

**Excluded on purpose** — because they are server-managed, and the repo copy would overwrite the staging config:

- `credentials.py` — SECRET_KEY, DB password
- `aimtravel_site/__init__.py` — PyMySQL shim (`install_as_MySQLdb`)
- `aimtravel_site/settings.py` — patched with `DEBUG=False`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, DATABASES-from-credentials, WhiteNoise middleware
- `passenger_wsgi.py` — real Django loader (cPanel would ship a 164-byte placeholder)
- `.htaccess`, `tmp/`, `public/` — Passenger-owned
- `.well-known/` — AutoSSL

If you edited one of these files in the repo, do NOT try to rsync it — edit it directly on the server using the templates in [file-templates.md](file-templates.md).

---

## 4. Extract Vite bundle (cPanel Terminal, ONLY if you uploaded a zip manually)

Skip this if the build was committed to git in step 2 — the bundle arrived through rsync already.

```bash
cd /home/aimtrave/staging.aimtravel.bg/static
unzip -o dist.zip
rm dist.zip
ls -la dist/
cd ..
```

---

## 5. Django management commands (cPanel Terminal)

```bash
cd /home/aimtrave/staging.aimtravel.bg
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py check
```

Expected: `check` prints `System check identified no issues (0 silenced).`. If it errors, jump to [known-failures.md](known-failures.md).

---

## 6. Restart Passenger (cPanel Terminal)

```bash
cd /home/aimtrave/staging.aimtravel.bg
touch tmp/restart.txt
```

If `tmp/` is missing — Passenger app was destroyed. See known-failures.md #6.

---

## 7. HTTP validation (Mac terminal)

`curl` from the server is blocked (Superhosting policy). Run from the Mac:

```bash
curl -sI https://staging.aimtravel.bg/zapisvane-za-brigada/
curl -s https://staging.aimtravel.bg/zapisvane-za-brigada/ | grep -E 'apply-[A-Za-z0-9_-]+\.(js|css)|<title>'
```

Expect `HTTP/2 200` + `x-powered-by: Phusion Passenger(R)`, and the second command to show the current bundle hashes plus the Bulgarian title.

The homepage `/` is expected to return 500 (MainSlider seed missing). Do not test on `/`.

---

## Quick verification when the site breaks after a deploy

Run these on the server, in order, and stop at the first surprise:

```bash
# 1. File integrity — everything the site needs is present and readable
ls -la /home/aimtrave/staging.aimtravel.bg/{.htaccess,passenger_wsgi.py,credentials.py}
ls -la /home/aimtrave/staging.aimtravel.bg/aimtravel_site/__init__.py

# 2. Permissions — Apache can traverse and read
ls -ld /home/aimtrave/staging.aimtravel.bg

# 3. Vite manifest — django-vite can render script tags
ls -la /home/aimtrave/staging.aimtravel.bg/staticfiles/dist/manifest.json
cat /home/aimtrave/staging.aimtravel.bg/staticfiles/dist/manifest.json

# 4. Virtualenv still has Django (cPanel sometimes wipes it silently)
source /home/aimtrave/virtualenv/staging.aimtravel.bg/3.11/bin/activate
pip show django | head -2

# 5. Django loads through passenger_wsgi.py (same code path as Apache)
python -c "
import sys
sys.path.insert(0, '/home/aimtrave/staging.aimtravel.bg')
from passenger_wsgi import application
print(type(application).__name__)
"

# 6. Django-level request against the real host (test client mimics Apache)
python <<'PYEOF'
import os, sys, traceback
sys.path.insert(0, "/home/aimtrave/staging.aimtravel.bg")
os.environ["DJANGO_SETTINGS_MODULE"] = "aimtravel_site.settings"
import django; django.setup()
from django.test import Client
c = Client(HTTP_HOST="staging.aimtravel.bg")
try:
    resp = c.get("/zapisvane-za-brigada/")
    print("Status:", resp.status_code)
except Exception:
    traceback.print_exc()
PYEOF
```

Whichever check fails first tells you which section of known-failures.md to open.
