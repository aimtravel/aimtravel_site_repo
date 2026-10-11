#!/bin/bash
# Production deploy for https://aimtravel.bg — run by cPanel through .cpanel.yml
# when the "Deploy to production" GitHub workflow calls
# VersionControlDeployment/create for the cPanel repo below.
#
#   1. preflight   credentials.py present; refuse to run from any other repo;
#                  if the commit has frontend/, its build (uploaded by the workflow
#                  as ~/deploy-state/frontend-<sha>.tar.gz + .sha256) must be intact
#   2. backup      code + database into ~/deploy-backups/<time>-<sha> (last 5 kept)
#   3. sync        aimtravel_site/, templates/, static/ and root files into the app,
#                  then the frontend build into static/dist
#   4. packages    pip install, only when requirements-production.txt changed
#   5. django      migrate, collectstatic (into public_html/static), check
#   6. restart     touch tmp/restart.txt (Passenger)
#
# Any failure after the backup restores the previous code and restarts the app
# (the database backup is kept for a manual restore if a migration ran).
# A file ~/deploy-state/ROLLBACK naming a backup makes the next run restore that
# backup instead of deploying — the workflow uses it when the live smoke test fails.
# The outcome is written to ~/deploy-state/last-deploy.txt for the workflow.
set -uo pipefail
# New files (synced code, collected static served by Apache) must be world-readable;
# existing files keep their permissions (rsync without -p).
umask 022

REPO=${DEPLOY_REPO:-/home/aimtrave/repositories/aimtravel-production}
APP=${DEPLOY_APP:-/home/aimtrave/aimtravel_site}
PY=${DEPLOY_PY:-/home/aimtrave/virtualenv/aimtravel_site/3.11/bin/python}
STATE=${DEPLOY_STATE:-/home/aimtrave/deploy-state}
BACKUPS=${DEPLOY_BACKUPS:-/home/aimtrave/deploy-backups}
KEEP_BACKUPS=5

CODE_DIRS="aimtravel_site templates static"
ROOT_FILES="manage.py passenger_wsgi.py requirements.txt requirements-production.txt Robots.txt"
# Never shipped and never deleted on the server: secrets, caches, uploads, archives.
EXCLUDES=(--exclude='__pycache__/' --exclude='*.pyc' --exclude='.idea/' --exclude='media/'
          --exclude='private_media/' --exclude='*credentials*.py' --exclude='.env*'
          --exclude='settings?*.py' --exclude='*.zip' --exclude='*.rar' --exclude='*.log'
          --exclude='*.sqlite3' --exclude='~$*')
# aimtravel_site/ may also hold documents that were never exported to git.
APP_DOC_EXCLUDES=(--exclude='*.pdf' --exclude='*.doc' --exclude='*.docx' --exclude='*.xls'
                  --exclude='*.xlsx' --exclude='*.csv')

log() { echo "[$(date -u +%H:%M:%S)] $*"; }
SHA=unknown; BK=""
status() {  # status <state> [detail]
  printf 'sha=%s\nstate=%s\nat=%s\nbackup=%s\ndetail=%s\n' \
    "$SHA" "$1" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$BK" "${2:-}" > "$STATE/last-deploy.txt"
}
restart_app() { mkdir -p "$APP/tmp" && touch "$APP/tmp/restart.txt"; }
sha256() { if command -v sha256sum >/dev/null; then sha256sum "$1"; else shasum -a 256 "$1"; fi | cut -d' ' -f1; }

sync_tree() {  # sync_tree <source root>  — mirror the code dirs + root files into $APP
  local src=$1 d f extra
  for d in $CODE_DIRS; do
    [ -d "$src/$d" ] || continue
    extra=(); [ "$d" = aimtravel_site ] && extra=("${APP_DOC_EXCLUDES[@]}")
    rsync -rlt --delete "${EXCLUDES[@]}" ${extra[@]+"${extra[@]}"} "$src/$d/" "$APP/$d/" || return 1
  done
  for f in $ROOT_FILES; do
    [ -f "$src/$f" ] && { cp "$src/$f" "$APP/$f" && chmod 644 "$APP/$f" || return 1; }
  done
  return 0
}

install_frontend() {  # install_frontend <build tar.gz>  — mirror it into static/dist
  local tmp rc
  tmp=$(mktemp -d "$BACKUPS/.frontend-XXXXXX") || return 1
  tar -xzf "$1" -C "$tmp" && [ -s "$tmp/manifest.json" ] \
    && mkdir -p "$APP/static/dist" && rsync -rlt --delete "$tmp/" "$APP/static/dist/"
  rc=$?
  rm -rf "$tmp"
  return $rc
}

restore_code() {  # restore_code <backup dir>
  local b=$1 tmp
  [ -f "$b/code.tar.gz" ] || { log "no code backup in $b"; return 1; }
  tmp=$(mktemp -d "$BACKUPS/.restore-XXXXXX") || return 1
  tar -xzf "$b/code.tar.gz" -C "$tmp" && sync_tree "$tmp"
  local rc=$?
  rm -rf "$tmp"
  return $rc
}

fail() {  # fail <step>  — after the backup exists: put the previous code back
  log "FAILED at: $1 — restoring previous code from $BK"
  if restore_code "$BK" && restart_app; then
    status failed_restored "$1 failed; previous code restored. Database backup: $BK/db.sql.gz"
  else
    status failed_restore_failed "$1 failed AND restoring $BK failed — needs manual action"
  fi
  exit 1
}

# ---------------------------------------------------------------- 1. preflight
mkdir -p "$STATE" "$BACKUPS" && chmod 700 "$STATE" "$BACKUPS"
if [ "$(pwd -P)" != "$(cd "$REPO" 2>/dev/null && pwd -P)" ]; then
  echo "Refusing: this .cpanel.yml deploys production only from $REPO (running in $(pwd -P))."
  exit 1
fi
SHA=$(git -C "$REPO" rev-parse HEAD)
log "deploy $SHA from $REPO into $APP"

if [ -f "$STATE/ROLLBACK" ]; then
  BK=$(tr -d '[:space:]' < "$STATE/ROLLBACK"); rm -f "$STATE/ROLLBACK"
  case "$BK" in "$BACKUPS"/*) ;; *) status rollback_failed "invalid backup path"; exit 1 ;; esac
  log "ROLLBACK requested: restoring $BK"
  if restore_code "$BK" && restart_app; then
    status rolled_back "code restored from $BK; database unchanged (backup: $BK/db.sql.gz)"; exit 0
  fi
  status rollback_failed "restoring $BK failed — needs manual action"; exit 1
fi

if ! ( cd "$APP" && "$PY" -c "import credentials as c; [c.SECRET_KEY, c.DB_NAME, c.DB_USER, c.DB_PASSWORD, c.EMAIL_HOST_USER, c.EMAILPASSWORD]" ) 2>/dev/null; then
  status failed_preflight "$APP/credentials.py missing or incomplete — nothing was changed"
  log "credentials.py missing or incomplete — aborting before any change"; exit 1
fi

FE=""
if [ -f "$REPO/frontend/package.json" ]; then
  FE="$STATE/frontend-$SHA.tar.gz"
  if [ ! -f "$FE" ] || [ "$(sha256 "$FE")" != "$(cut -d' ' -f1 "$FE.sha256" 2>/dev/null)" ]; then
    status failed_preflight "frontend build $(basename "$FE") missing or damaged — nothing was changed"
    log "frontend build for $SHA missing or damaged — aborting before any change"; exit 1
  fi
fi

# ---------------------------------------------------------------- 2. backup
BK="$BACKUPS/$(date -u +%Y%m%d-%H%M%S)-${SHA:0:7}"
mkdir -p "$BK" && chmod 700 "$BK" || { status failed_backup "cannot create $BK"; exit 1; }
status in_progress "backing up"
existing=(); for p in $CODE_DIRS $ROOT_FILES; do [ -e "$APP/$p" ] && existing+=("$p"); done
if ! tar -czf "$BK/code.tar.gz" -C "$APP" --exclude='__pycache__' --exclude='*.pyc' ${existing[@]+"${existing[@]}"}; then
  status failed_backup "code backup failed — nothing was changed"; exit 1
fi
# Option-file values are double-quoted (an unquoted '#' or ';' starts a comment)
# with backslash and double quote escaped.
( umask 077; cd "$APP" && "$PY" - > "$BK/.my.cnf" <<'PY'
import credentials as c
def opt(v): return '"' + str(v).replace('\\', '\\\\').replace('"', '\\"') + '"'
print('[client]'); print('user=' + opt(c.DB_USER)); print('password=' + opt(c.DB_PASSWORD))
print('host=' + opt(getattr(c, 'DB_HOST', 'localhost'))); print('port=' + str(getattr(c, 'DB_PORT', '3306')))
PY
)
DB_NAME=$(cd "$APP" && "$PY" -c "import credentials as c; print(c.DB_NAME)")
if ! mysqldump --defaults-extra-file="$BK/.my.cnf" --single-transaction --quick --no-tablespaces "$DB_NAME" | gzip > "$BK/db.sql.gz" \
   || [ ! -s "$BK/db.sql.gz" ]; then
  rm -f "$BK/.my.cnf"; status failed_backup "database backup failed — nothing was changed"; exit 1
fi
rm -f "$BK/.my.cnf"
log "backup ok: $BK ($(du -sh "$BK" | cut -f1))"
ls -1d "$BACKUPS"/*/ 2>/dev/null | sort | awk -v k="$KEEP_BACKUPS" '{a[NR]=$0} END {for (i = 1; i <= NR - k; i++) print a[i]}' \
  | while IFS= read -r old; do rm -rf "$old"; done

# ---------------------------------------------------------------- 3. sync
status in_progress "syncing code"
sync_tree "$REPO" || fail "code sync"
if [ -n "$FE" ]; then
  status in_progress "installing frontend build"
  install_frontend "$FE" || fail "frontend install"
fi

# ---------------------------------------------------------------- 4. packages
REQ_HASH=$([ -f "$APP/requirements-production.txt" ] && sha256 "$APP/requirements-production.txt")
if [ -n "$REQ_HASH" ] && [ "$REQ_HASH" != "$(cat "$STATE/requirements.sha256" 2>/dev/null)" ]; then
  log "requirements-production.txt changed — pip install"
  "$PY" -m pip install -q -r "$APP/requirements-production.txt" || fail "pip install"
  echo "$REQ_HASH" > "$STATE/requirements.sha256"
fi

# ---------------------------------------------------------------- 5. django
cd "$APP" || fail "cd $APP"
status in_progress "migrate"
"$PY" manage.py migrate --noinput || fail "migrate"
"$PY" manage.py collectstatic --noinput || fail "collectstatic"
"$PY" manage.py check || fail "manage.py check"

# ---------------------------------------------------------------- 6. restart
restart_app || fail "restart"
status ok "deployed"
find "$STATE" -maxdepth 1 -name 'frontend-*.tar.gz*' ! -name "frontend-$SHA.tar.gz*" -delete
log "deploy ok: $SHA"
