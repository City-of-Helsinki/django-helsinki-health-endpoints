import os

DEBUG = True

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

INSTALLED_APPS = [
    "helsinki_health_endpoints",
]

ROOT_URLCONF = "helsinki_health_endpoints.tests.urls"

SECRET_KEY = "test-secret-key-not-for-production"  # noqa: S105

USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
