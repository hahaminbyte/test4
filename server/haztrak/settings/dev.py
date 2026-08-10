"""Settings for development environment."""

import os

from .base import *  # noqa: F403, S105, RUF100

# General
SECRET_KEY = "django-insecure-%btjqoun@6ps$e@8bw$48s+!x1e4aiz&5p2nrf6cmiw4)jsx5d"
DEBUG = True
CORS_ORIGIN_WHITELIST = [
    os.getenv("HT_CORS_DOMAIN", "http://localhost:3000"),
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
SESSION_COOKIE_SAMESITE = "Lax"

REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [  # noqa: F405
    "rest_framework.renderers.JSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
]

# Run Celery tasks in-process so npm start works without Redis/workers.
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# In-memory cache so waste-code / DOT lookups work without Redis.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "haztrak-dev",
    },
}

# Database
# https://docs.djangoproject.com/en/stable/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": os.environ.get("HT_DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.environ.get("HT_DB_NAME", "db.sqlite3"),
        "USER": os.environ.get("HT_DB_USER", "admin"),
        "PASSWORD": os.environ.get("HT_DB_PASSWORD", "password"),
        "HOST": os.environ.get("HT_DB_HOST", "localhost"),
        "PORT": os.environ.get("HT_DB_PORT", "5432"),
    },
}
FIXTURE_DIRS = ["fixtures"]

# Haztrak settings — default preprod; override with HT_RCRAINFO_ENV if set
if "HT_RCRAINFO_ENV" not in os.environ:
    os.environ["HT_RCRAINFO_ENV"] = "PREPROD"
