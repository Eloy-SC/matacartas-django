"""
Test settings that use SQLite instead of PostgreSQL.
Used for running tests without Docker: python manage.py test --settings=matacartas.test_settings
"""
from .settings import *  # noqa: F401, F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
