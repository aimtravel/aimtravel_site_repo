---
name: redeploy-staging
description: Redeploy the current branch of aimtravel_site to https://staging.aimtravel.bg (Superhosting/cPanel + Passenger + Django 4.1 + Vite + WhiteNoise). Walks preflight → deploy → validation → recovery, one step at a time, pasting server commands into the user's cPanel Terminal because SSH from the laptop is blocked. Use whenever the user says "redeploy staging", "push to staging", "deploy the changes to staging.aimtravel.bg", or reports staging is broken and needs to be fixed.
---

# Redeploy staging.aimtravel.bg

You are helping the user deploy the current git branch of `aimtravel_site` to `https://staging.aimtravel.bg`. The staging environment is on **Superhosting shared hosting** with **cPanel + Phusion Passenger + Python 3.11 (CloudLinux Python Selector)**. SSH from the user's Mac is BLOCKED — server commands are executed by the user in **cPanel Terminal**, and you receive the pasted output.

## Environment constants

- Server user: `aimtrave` (cPanel account)
- App root on server: `/home/aimtrave/staging.aimtravel.bg/`
- Git working copy on server: `/home/aimtrave/repos/aimtravel-site/`
- Virtualenv on server: `/home/aimtrave/virtualenv/staging.aimtravel.bg/3.11/`
- Local repo on Mac: `/Users/sstoy2/aimtravel_site_repo/`
- Public URL: `https://staging.aimtravel.bg/`
- Target feature route: `https://staging.aimtravel.bg/zapisvane-za-brigada/`
- Homepage (`/`) is EXPECTED to 500 on staging (empty DB — no MainSlider row). Test on the feature route, not `/`.

## Prerequisites you must confirm before starting

Before any commands, load [references/known-failures.md](references/known-failures.md) and [references/file-templates.md](references/file-templates.md) so you have the recovery table and the file contents in hand.

Ask the user (only if not already stated) which of these are in scope this run:
1. **Backend-only change** (Python files) → skip Vite build.
2. **Frontend change** (files under `frontend/src/`) → include Vite build + upload dance.
3. **Both** → full pipeline.

## Workflow

Do these phases in order. After each phase, wait for the user to paste output before proceeding. Never fire the next phase's commands until the current one's output confirms success.

### Phase 1 — Local preflight (Mac)

Run all of these yourself via Bash (do not delegate):

```bash
cd /Users/sstoy2/aimtravel_site_repo
git status --short
git log -1 --oneline
git rev-parse --abbrev-ref HEAD
```

**Gate:** working tree must be clean OR the changes the user wants to deploy must be committed AND pushed to origin. If `git status` shows M/D/?? lines that the user hasn't acknowledged, stop and ask. If the branch head hasn't been pushed (check with `git status` — "Your branch is ahead of 'origin/…'"), tell the user to push before continuing:

```bash
git push origin <branch-name>
```

Never call `git push` yourself without the user's word.

### Phase 2 — Frontend build (Mac, ONLY if frontend changed)

Skip this entire phase for backend-only deploys.

```bash
cd /Users/sstoy2/aimtravel_site_repo/frontend
./node_modules/.bin/vite build
```

**Not** `npm run build` — that runs `tsc -b && vite build`, and the TypeScript pass fails on a known bug in `src/apply/DateOfBirthPicker.tsx` (a wrong `as "errors.required"` cast). Runtime behaviour is identical.

**Gate:** output shows `../static/dist/manifest.json` and `../static/dist/assets/apply-*.{js,css}` — no errors. Then zip:

```bash
cd /Users/sstoy2/aimtravel_site_repo/static
rm -f dist.zip
zip -r dist.zip dist/
ls -la dist.zip
```

Tell the user:

> **Upload `/Users/sstoy2/aimtravel_site_repo/static/dist.zip` via cPanel File Manager → navigate to `/home/aimtrave/staging.aimtravel.bg/static/` → Upload → drag `dist.zip`.**

Wait for confirmation before continuing.

### Phase 3 — Server pull + rsync (cPanel Terminal)

Give the user this single block to paste. It activates the venv, pulls latest, and rsyncs with the correct excludes. Note `-rlt` (not `-a`) — `-a` preserves permissions and would break `.htaccess`, which is what caused the Forbidden loop last time.

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

Wait for the output. Gate: `git pull` shows either "Already up to date" or a fast-forward summary; `rsync` finishes without `link_stat failed` or `permission denied`.

If the Python file being redeployed is one of the excluded ones (`settings.py`, `__init__.py`, `credentials.py`, `passenger_wsgi.py`) tell the user directly — those are server-managed and need a targeted edit, not an rsync. Fall back to [references/file-templates.md](references/file-templates.md) and give them the exact `python <<'PYEOF'` block to patch it.

### Phase 4 — Extract Vite bundle (cPanel Terminal, ONLY if Phase 2 ran)

```bash
cd /home/aimtrave/staging.aimtravel.bg/static
unzip -o dist.zip
rm dist.zip
ls -la dist/
cd ..
```

Gate: `dist/manifest.json` and `dist/assets/apply-*.{js,css}` present.

### Phase 5 — Django management commands (cPanel Terminal)

```bash
cd /home/aimtrave/staging.aimtravel.bg
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py check
```

Gate: `check` returns `System check identified no issues (0 silenced).`

**If `check` fails with `ModuleNotFoundError`** — the venv was reset by cPanel (see [references/known-failures.md](references/known-failures.md), failure #7). Reinstall packages using the block in that file.

**If `check` fails with `ImproperlyConfigured` or `credentials`-related error** — one of the server-managed files (credentials.py, __init__.py, settings.py) is missing or reverted. See file templates.

### Phase 6 — Restart Passenger (cPanel Terminal)

```bash
cd /home/aimtrave/staging.aimtravel.bg
touch tmp/restart.txt
ls -la tmp/restart.txt
```

Gate: file exists with the current timestamp.

If `tmp/` does not exist (`touch: cannot touch 'tmp/restart.txt': No such file or directory`) — the Passenger app was destroyed (Failure #6). Follow the recovery in [references/known-failures.md](references/known-failures.md).

### Phase 7 — HTTP validation (Mac)

Run yourself. Do NOT ask the user to run curl on the server — it is blocked (`Permission denied: '/bin/curl'`).

```bash
curl -sI https://staging.aimtravel.bg/zapisvane-za-brigada/
```

**Expected:**
```
HTTP/2 200
x-powered-by: Phusion Passenger(R) 6.1.8
content-type: text/html; charset=utf-8
```

**Then** verify Vite manifest resolved into HTML (proves the React island can boot):

```bash
curl -s https://staging.aimtravel.bg/zapisvane-za-brigada/ | grep -E 'apply-[A-Za-z0-9_-]+\.(js|css)|<title>'
```

Expected: at least one `apply-<hash>.js`, one `apply-<hash>.css`, and the Bulgarian `<title>`.

If any status other than 200 comes back, jump to [references/known-failures.md](references/known-failures.md) — the table there maps status/header/body to root cause.

### Phase 8 — Confirmation to user

When Phase 7 passes, tell the user:
1. The URL to test: `https://staging.aimtravel.bg/zapisvane-za-brigada/`
2. What commit is now live (from Phase 1's `git log -1`).
3. Any Phase 5 warnings that need eventual attention (e.g., `check --deploy` HSTS warnings).

Do not claim the homepage works — it will 500 until MainSlider is seeded. Only the feature route is the promise.

## Constraints for you

- **Never** run cleanup commands (`rm`, `find -delete`, `git restore .`) on files you did not create in this session unless the user explicitly asks.
- **Never** paste `...` placeholders in commands the user will run. Every rsync exclude, every path, spelled out.
- **Never** claim deploy is done based on your own optimism — Phase 7 curl from the Mac is the only source of truth.
- When user pastes server output, read it line by line. If a line contains `Permission denied`, `No such file or directory`, `ModuleNotFoundError`, or `Traceback`, stop and diagnose — do not proceed to the next phase.
- When you edit `emails.py`, `settings.py`, `__init__.py`, `credentials.py` or `passenger_wsgi.py`, be explicit about whether the edit belongs in git (committable) or is server-only (staging config).
- If the user opens the cPanel Setup Python App page and it says "No such application" — the app was destroyed. Follow the recovery in [references/known-failures.md](references/known-failures.md).
