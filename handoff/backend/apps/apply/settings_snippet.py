"""Какво да се добави в settings.py на проекта.

НЕ е самостоятелен модул — Devin трябва да разнесе тези парчета по
съответните секции на съществуващия settings.py.
"""

# --- 1. Приложения -----------------------------------------------------------
INSTALLED_APPS_ADD = [
    "rest_framework",
    "django_vite",
    "apps.apply",
]

# --- 2. django-vite ----------------------------------------------------------
# DEV_MODE=True кара template тага да сочи към Vite dev сървъра (HMR).
# В продукция чете от manifest.json, който Vite build-ът е произвел.
DJANGO_VITE = {
    "default": {
        "dev_mode": "DEBUG",                  # → env, не литерал
        "dev_server_port": 5173,
        "manifest_path": "static/dist/manifest.json",
        "static_url_prefix": "dist",
    }
}
STATICFILES_DIRS_ADD = ["static"]             # тук Vite пише build-а

# --- 3. DRF ------------------------------------------------------------------
REST_FRAMEWORK_ADD = {
    "DEFAULT_THROTTLE_RATES": {
        "apply_burst": "5/min",
        "apply_day": "20/day",
        "lookup": "120/min",
    },
}

# --- 4. Кеш ------------------------------------------------------------------
# ЗАДЪЛЖИТЕЛНО Redis: DRF throttling пази броячите в кеша, а LocMemCache
# е локален за всеки gunicorn процес — с 4 работника лимитът става 4×.
CACHES_NOTE = "django.core.cache.backends.redis.RedisCache"

# --- 5. Бизнес настройки -----------------------------------------------------
AIM_MANAGER_NAME = "Росен Антонов"
AIM_COMPANY_UIC = "203634922"
AIM_FROM_EMAIL = "studentski@aimtravel.bg"
SITE_URL = "https://aimtravel.bg"

AIM_CONTRACT_TEMPLATES = "media/contract_templates"   # contract_2027.docx, …
AIM_STATIC_DOCS = "media/static_docs"                 # Resume_blank_AIM.docx, …

AIM_OFFICE_AGENTS = {
    "varna": {"name": "Стоян Стоянов", "email": "varna@aimtravel.bg",
              "phone": "+359 88 99 66 583"},
    "sofia": {"name": "—", "email": "sofia@aimtravel.bg",
              "phone": "+359 88 99 66 583"},
}

# --- 6. Turnstile ------------------------------------------------------------
TURNSTILE_SITE_KEY = ""      # от env
TURNSTILE_SECRET_KEY = ""    # от env — НИКОГА в кода
TURNSTILE_DISABLED = False   # True само в тестове

# --- 7. Celery beat ----------------------------------------------------------
CELERY_BEAT_SCHEDULE_ADD = {
    "purge-stale-apply-drafts": {
        "task": "apps.apply.tasks.purge_stale_drafts",
        "schedule": 24 * 60 * 60,     # веднъж дневно
    },
}
