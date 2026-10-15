import functools
import tomllib
from pathlib import Path

from django.conf import settings
from django.db import connection


@functools.cache
def _get_version() -> str:
    try:
        pyproject_path = Path(settings.BASE_DIR) / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        return data["project"]["version"]
    except Exception:
        return "unknown"


def _check_database() -> str:
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return "ok"
    except Exception:
        return "error"
