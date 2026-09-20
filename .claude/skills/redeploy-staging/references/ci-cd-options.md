# CI/CD options for staging.aimtravel.bg

Analysis of what can and cannot be automated with GitHub Actions on Superhosting shared hosting. Ordered from most-recommended to least-recommended.

## The core constraint

Superhosting shared plans **block inbound SSH from external hosts** (the whole reason SSH from the Mac fails). GitHub Actions runners cannot SSH into the server either. Every automation pattern has to work around this. That leaves three viable channels:

1. **cPanel Git Version Control** — the server itself pulls from GitHub. No inbound connection needed. Combined with a `.cpanel.yml` deploy manifest, the pull triggers the deploy commands.
2. **HTTP webhook** — a script on the server (PHP, since PHP is always available) exposes an endpoint that GitHub Actions calls after a push. The script runs the deploy commands under the account user.
3. **SFTP** — copy files up via GitHub Actions. But this only moves files; it can't run `python manage.py migrate` or `touch tmp/restart.txt`, so it needs to be paired with #1 or #2 anyway.

There is no fourth channel. If none of these fit, the deploy stays manual.

---

## Option 1 — cPanel Git Version Control + `.cpanel.yml` (recommended)

**What it does:** cPanel's Git Version Control feature has a built-in "Deploy from remote" action. When you add a `.cpanel.yml` file to your repo, cPanel runs the commands listed there against the pulled-out working copy. You can trigger the deploy manually via cPanel UI OR call cPanel's UAPI from GitHub Actions.

**Setup on the server (one-time):**

1. cPanel → **Git Version Control** → find `/home/aimtrave/repos/aimtravel-site` (already configured from initial deploy). If not, click **Create** and clone from the public GitHub URL: `https://github.com/vlzahariev/aimtravel_site_repo.git`, branch `feature/implement-new-application-form` (or `main` when merged).
2. Enable **Automatic Deployment** — a toggle in the repo settings inside cPanel.

**Setup in the repo:**

Add `.cpanel.yml` at the repo root (this file IS committed to git). Example:

```yaml
---
deployment:
  tasks:
    - export DEPLOYPATH=/home/aimtrave/staging.aimtravel.bg/
    - export VENV=/home/aimtrave/virtualenv/staging.aimtravel.bg/3.11/bin

    # 1. Sync source (same rsync + excludes as manual deploy)
    - /usr/bin/rsync -rlt \
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
        ./ $DEPLOYPATH

    # 2. Django management commands
    - cd $DEPLOYPATH && $VENV/python manage.py migrate --noinput
    - cd $DEPLOYPATH && $VENV/python manage.py collectstatic --noinput

    # 3. Restart Passenger
    - touch $DEPLOYPATH/tmp/restart.txt
```

**Setup in GitHub (optional — for full push-to-deploy):**

Add `.github/workflows/deploy-staging.yml`:

```yaml
name: Deploy to staging
on:
  push:
    branches: [feature/implement-new-application-form]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger cPanel deploy
        run: |
          curl -sSf -H "Authorization: cpanel ${{ secrets.CPANEL_USER }}:${{ secrets.CPANEL_TOKEN }}" \
            "https://your-cpanel-host:2083/execute/VersionControlDeployment/create?repository_root=%2Fhome%2Faimtrave%2Frepos%2Faimtravel-site"
```

You need to generate a cPanel API token: **cPanel → Manage API Tokens → Create**, save name + token as GitHub Secrets `CPANEL_USER` and `CPANEL_TOKEN`.

**Pros:**
- No external SSH needed.
- Deploy commands live in the repo as code (`.cpanel.yml`), reviewable and version-controlled.
- Fully hands-off after setup — push to branch, wait ~30 seconds, staging updated.

**Cons:**
- Server-managed files (`credentials.py`, patched `settings.py`, PyMySQL shim in `__init__.py`, `passenger_wsgi.py`) still have to exist on the server before the first automated deploy — they cannot come from the repo.
- Debugging failed deploys is limited (cPanel UI shows a small log window; no live tail).
- Frontend build has to happen SOMEWHERE. Either: (a) the GitHub Actions job builds and pushes the bundle to the branch before triggering deploy, (b) `.cpanel.yml` runs the build on the server (needs Node.js, may not be installed), or (c) you commit the build manually before push.

**Recommended variant (a) — build in GitHub Actions:**

```yaml
name: Deploy to staging
on:
  push:
    branches: [feature/implement-new-application-form]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      - run: cd frontend && npm ci
      - run: cd frontend && ./node_modules/.bin/vite build
      - name: Commit bundle
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add static/dist/manifest.json 'static/dist/assets/apply-*'
          git diff --cached --quiet || git commit -m "chore(build): rebuild Vite bundle [skip ci]"
          git push
      - name: Trigger cPanel deploy
        run: |
          curl -sSf -H "Authorization: cpanel ${{ secrets.CPANEL_USER }}:${{ secrets.CPANEL_TOKEN }}" \
            "https://your-cpanel-host:2083/execute/VersionControlDeployment/create?repository_root=%2Fhome%2Faimtrave%2Frepos%2Faimtravel-site"
```

`[skip ci]` in the commit message prevents infinite loops (the auto-commit push doesn't retrigger the workflow).

---

## Option 2 — HTTP webhook + PHP dispatcher (fallback if cPanel Git Version Control is not available)

Only worth pursuing if Option 1's `.cpanel.yml` support turns out to be missing or broken on this plan.

**Server side:** create `~/staging.aimtravel.bg/public/_deploy.php` (yes, in the Apache-served docroot, but path-protected):

```php
<?php
if (!hash_equals($_SERVER['HTTP_X_DEPLOY_TOKEN'] ?? '', 'THE_SECRET')) {
    http_response_code(403);
    exit('forbidden');
}
$out = shell_exec('cd /home/aimtrave/repos/aimtravel-site && git pull && '
    . 'rsync -rlt --exclude=".git" ... /home/aimtrave/repos/aimtravel-site/ /home/aimtrave/staging.aimtravel.bg/ && '
    . 'cd /home/aimtrave/staging.aimtravel.bg && '
    . 'source /home/aimtrave/virtualenv/staging.aimtravel.bg/3.11/bin/activate && '
    . 'python manage.py migrate --noinput 2>&1 && '
    . 'python manage.py collectstatic --noinput 2>&1 && '
    . 'touch tmp/restart.txt 2>&1');
echo $out;
```

GitHub Actions calls it:

```yaml
- name: Trigger deploy
  run: curl -sSf -X POST -H "X-Deploy-Token: ${{ secrets.DEPLOY_TOKEN }}" https://staging.aimtravel.bg/_deploy.php
```

**Pros:** works without any special cPanel feature.
**Cons:**
- The `_deploy.php` endpoint is a real attack surface. Strong secret, header check, rate limit, log every call.
- `shell_exec` availability varies by hosting; Superhosting may have it disabled.
- Debugging is via HTTP response only — the output PHP prints back to the workflow log.

Skip this if Option 1 works.

---

## Option 3 — SFTP file sync via GitHub Actions (files only, not enough on its own)

`SamKirkland/FTP-Deploy-Action` and similar can push files to the server over SFTP. They can NOT:
- run `python manage.py migrate`
- run `python manage.py collectstatic`
- restart Passenger

So on its own, SFTP-sync gives you incomplete deploys — every deploy still needs a manual cPanel Terminal session for the Django/Passenger steps. That is worse than the current manual runbook, not better.

Only useful in combination with Option 2 (SFTP for files, webhook for `migrate`/`restart`), and even then, Option 1 already does both together.

---

## What CI/CD cannot cover — the manual escape hatches

Some situations need cPanel Terminal (or the UI) no matter what automation is set up:

- **cPanel wipes the Python App or its virtualenv** — must be recreated via **Setup Python App → CREATE APPLICATION**. There is no cPanel API endpoint that reliably recreates the app with the exact right startup file / entry point.
- **The server-managed files diverge or are lost** — `credentials.py`, patched `settings.py`, PyMySQL shim, `passenger_wsgi.py` must be restored from [file-templates.md](file-templates.md). Do not put these in git; do not automate their creation from a workflow (they contain a secret and per-environment overrides).
- **Full package reinstall after venv reset** — the strip list from [known-failures.md](known-failures.md) #7 has to run on the server.
- **Diagnosing an active 500 or 403** — the Django test-Client trick and `ls -la`/`chmod` recovery steps must happen with a real shell.

For these, cPanel Terminal is the tool; there is no automation shortcut that avoids it.

---

## Recommendation

For this project, at this scale:

1. **Now, before any automation** — the manual playbook (`SKILL.md` + `cheatsheet.md`) works reliably. Every step is scripted; the human is a copy-paste operator, not a diagnostician.
2. **When the staging deploys happen more than once per day** — set up Option 1 (`.cpanel.yml` + GitHub Actions with build step). Estimate: half a day of setup, including generating a cPanel API token, verifying `.cpanel.yml` runs the rsync correctly the first time, and confirming the webhook returns a success code.
3. **Never rely on automation without the manual escape hatch** — keep this skill and its references intact so the moment CI/CD breaks (and it will), the fallback is a copy-pasteable runbook, not "let me remember what to do".
