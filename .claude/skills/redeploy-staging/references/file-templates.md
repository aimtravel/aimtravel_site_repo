# File templates — server-managed configs

These files live ONLY on the server (excluded from rsync, not in git). When they are missing or reverted, restore them from these templates. Do not commit these to the repo.

Ask the user for anything unknown (a new DB password after rotation, a new SECRET_KEY, etc.) — never invent placeholder values.

---

## `credentials.py`

Path on server: `/home/aimtrave/staging.aimtravel.bg/credentials.py`
Permissions: `chmod 600` (owner-only)

Values as of the initial deploy (rotate if compromised):
- DB_NAME: `aimtrave_staging`
- DB_USER: `aimtrave_stgusr`
- DB_PASSWORD: (ask user or check password manager — was `apg%[j]zxwmxddoA` initially, may have been rotated)
- DB_HOST: `localhost`
- DB_PORT: `3306`
- SECRET_KEY: 50-char random string. Generate a new one when restoring, do NOT reuse the initial one if it was exposed. Command:
  ```bash
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```

Template to write (fill in the DB password and SECRET_KEY placeholders):

```python
"""Staging credentials for staging.aimtravel.bg.

NOT committed to the repo. Lives only on the server.
Rotate after any incident: change MySQL user password + regenerate SECRET_KEY.
"""

SECRET_KEY = "<REPLACE_WITH_NEW_KEY>"

# Outbound email: not configured on staging yet.
EMAILPASSWORD = ""

# MySQL — staging DB provisioned in cPanel MySQL Databases.
DB_NAME = "aimtrave_staging"
DB_USER = "aimtrave_stgusr"
DB_PASSWORD = "<REPLACE_WITH_DB_PASSWORD>"
DB_HOST = "localhost"
DB_PORT = "3306"
```

Server command to restore (paste into cPanel Terminal, replacing the two placeholders):

```bash
python <<'PYEOF'
import os
content = '''"""Staging credentials for staging.aimtravel.bg.

NOT committed to the repo. Lives only on the server.
"""

SECRET_KEY = "<REPLACE_WITH_NEW_KEY>"
EMAILPASSWORD = ""
DB_NAME = "aimtrave_staging"
DB_USER = "aimtrave_stgusr"
DB_PASSWORD = "<REPLACE_WITH_DB_PASSWORD>"
DB_HOST = "localhost"
DB_PORT = "3306"
'''
with open("/home/aimtrave/staging.aimtravel.bg/credentials.py", "w") as f:
    f.write(content)
os.chmod("/home/aimtrave/staging.aimtravel.bg/credentials.py", 0o600)
print("credentials.py written (chmod 600)")
PYEOF
```

---

## `aimtravel_site/__init__.py` (PyMySQL shim)

Path on server: `/home/aimtrave/staging.aimtravel.bg/aimtravel_site/__init__.py`

Purpose: replaces `mysqlclient` (which can't build without gcc on Superhosting) with `PyMySQL` (pure Python), so Django's `django.db.backends.mysql` backend works.

Content — exactly:
```python
import pymysql

pymysql.install_as_MySQLdb()
```

Server restore:
```bash
cat > /home/aimtrave/staging.aimtravel.bg/aimtravel_site/__init__.py << 'EOF'
import pymysql

pymysql.install_as_MySQLdb()
EOF
```

---

## `passenger_wsgi.py`

Path on server: `/home/aimtrave/staging.aimtravel.bg/passenger_wsgi.py`
Permissions: `chmod 644`

Purpose: Passenger's entry point. cPanel Setup Python App creates a 164-byte placeholder here; we replace it with a real Django loader.

Content — exactly:
```python
"""Passenger WSGI entry point for staging.aimtravel.bg."""

import os
import sys

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aimtravel_site.settings")

from aimtravel_site.wsgi import application  # noqa: E402
```

Server restore:
```bash
cat > /home/aimtrave/staging.aimtravel.bg/passenger_wsgi.py << 'EOF'
"""Passenger WSGI entry point for staging.aimtravel.bg."""

import os
import sys

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aimtravel_site.settings")

from aimtravel_site.wsgi import application  # noqa: E402
EOF
chmod 644 /home/aimtrave/staging.aimtravel.bg/passenger_wsgi.py
```

Sanity check that Django loads through this file:
```bash
python -c "
import sys
sys.path.insert(0, '/home/aimtrave/staging.aimtravel.bg')
from passenger_wsgi import application
print('type:', type(application).__name__)
"
```
Expected: `type: WSGIHandler`.

---

## `settings.py` patches (four edits)

Path on server: `/home/aimtrave/staging.aimtravel.bg/aimtravel_site/settings.py`

The repo version of `settings.py` is dev-configured (DEBUG=True, hardcoded root/mysql_pw DB). Staging needs four surgical edits. **Never edit repo `settings.py` for these — they are server-only.**

Patch script (idempotent — safely re-runnable):

```bash
python <<'PYEOF'
import shutil

path = "/home/aimtrave/staging.aimtravel.bg/aimtravel_site/settings.py"
shutil.copy(path, path + ".bak.staging")
text = open(path).read()
changes = []

# 1. DEBUG = True -> False
if "DEBUG = True" in text:
    text = text.replace("DEBUG = True", "DEBUG = False", 1)
    changes.append("DEBUG: True -> False")

# 2. ALLOWED_HOSTS + CSRF_TRUSTED_ORIGINS
old_hosts = '''ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
]'''
new_hosts = '''ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "staging.aimtravel.bg",
]

CSRF_TRUSTED_ORIGINS = [
    "https://staging.aimtravel.bg",
]'''
if old_hosts in text:
    text = text.replace(old_hosts, new_hosts)
    changes.append("ALLOWED_HOSTS + CSRF_TRUSTED_ORIGINS added")

# 3. DATABASES: hardcoded -> read from credentials
old_db = '''DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "aimtravel",
        "USER": "root",
        "PASSWORD": "mysql_pw",
        "HOST": "127.0.0.1",
        "PORT": "3306",
    }
}'''
new_db = '''DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": credentials.DB_NAME,
        "USER": credentials.DB_USER,
        "PASSWORD": credentials.DB_PASSWORD,
        "HOST": credentials.DB_HOST,
        "PORT": credentials.DB_PORT,
    }
}'''
if old_db in text:
    text = text.replace(old_db, new_db)
    changes.append("DATABASES: reads from credentials")

# 4. WhiteNoise middleware
old_mw = '''MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",'''
new_mw = '''MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",'''
if old_mw in text:
    text = text.replace(old_mw, new_mw)
    changes.append("WhiteNoise middleware added")

open(path, "w").write(text)
print("settings.py patches applied:")
for c in changes:
    print(f"  - {c}")
if not changes:
    print("  (none — file already patched)")
print(f"Backup: {path}.bak.staging")
PYEOF
```

---

## `.htaccess`

Path on server: `/home/aimtrave/staging.aimtravel.bg/.htaccess`
Permissions: `chmod 644`

**Do not write this by hand.** cPanel's Setup Python App generates it. If it is missing, the only reliable way to restore is to recreate the Python App through the cPanel UI (see failure #6 in [known-failures.md](known-failures.md)).

For reference, cPanel's generated content looks like:
```
# DO NOT REMOVE. CLOUDLINUX PASSENGER CONFIGURATION BEGIN
PassengerAppRoot "/home/aimtrave/staging.aimtravel.bg"
PassengerBaseURI "/"
PassengerPython "/home/aimtrave/virtualenv/staging.aimtravel.bg/3.11/bin/python"
# DO NOT REMOVE. CLOUDLINUX PASSENGER CONFIGURATION END
# DO NOT REMOVE OR MODIFY. CLOUDLINUX ENV VARS CONFIGURATION BEGIN
<IfModule Litespeed>
</IfModule>
# DO NOT REMOVE OR MODIFY. CLOUDLINUX ENV VARS CONFIGURATION END
```

If Python version, virtualenv path, or app root differ from these, it usually means a new app was created with different parameters — verify the cPanel UI shows the right settings before assuming the file is wrong.
