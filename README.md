# django-helsinki-health-endpoints

Reusable Django app providing unified `/healthz` and `/readiness` endpoints for City of Helsinki projects.

## Features

- `/healthz` — Kubernetes liveness probe (always returns HTTP 200)
- `/readiness` — Kubernetes readiness probe with:
  - Application version (read from `pyproject.toml`)
  - Database connectivity check
  - Sentry release tag

## Installation

```bash
pip install django-helsinki-health-endpoints
```

## Configuration

### 1. Add to `INSTALLED_APPS`

```python
INSTALLED_APPS = [
    # ...
    "helsinki_health_endpoints",
]
```

### 2. Include URL patterns

```python
from django.urls import include, path

urlpatterns = [
    path("", include("helsinki_health_endpoints.urls")),
    # ...
]
```

This registers `healthz` and `readiness` endpoints at the root. You can mount them under a prefix if needed:

```python
urlpatterns = [
    path("__", include("helsinki_health_endpoints.urls")),  # => /__healthz, /__readiness
]
```

You can also register the endpoints individually instead of using `include`:

```python
from helsinki_health_endpoints.views import healthz, readiness

urlpatterns = [
    path("healthz", healthz),
    path("readiness", readiness),
]
```

### 3. Settings

`helsinki_health_endpoints` reads the following keys from `django.conf.settings`:

| Setting | Required | Description |
|---|---|---|
| `BASE_DIR` | Yes | Project root directory, used to locate `pyproject.toml` for the version |
| `SENTRY_RELEASE` | No | Release tag/version string exposed in the `/readiness` response (default: `""`) |

`BASE_DIR` is typically already defined in your project's `settings.py`:

```python
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
```

To expose your Sentry release in the `/readiness` response, add:

```python
import os

SENTRY_RELEASE = os.environ.get("SENTRY_RELEASE", "")
```

## System checks

`helsinki_health_endpoints` registers Django [system checks](https://docs.djangoproject.com/en/stable/topics/checks/) that run automatically on startup (or via `manage.py check`).

| ID | Level | Description |
|---|---|---|
| `helsinki_health_endpoints.E001` | Error | `BASE_DIR` is not defined in settings. |
| `helsinki_health_endpoints.E002` | Error | `pyproject.toml` is excluded by `.dockerignore` (the file is required at runtime to read the package version). |
| `helsinki_health_endpoints.W001` | Warning | `.dockerignore` exists but could not be read (e.g. permission error). |

## Response examples

### `GET /healthz`

```
HTTP 200
```

### `GET /readiness`

```json
{
  "status": "ok",
  "packageVersion": "1.2.3",
  "release": "theapp@1.2.3",
  "database": "ok"
}
```

If the database check fails:

```json
HTTP 503

{
  "status": "error",
  "packageVersion": "1.2.3",
  "release": "theapp@1.2.3",
  "database": "error"
}
```

## Development

This project uses [Hatch](https://hatch.pypa.io/) for development, testing, and building.

### Install Hatch

```bash
pip install hatch
```

### Set up the development environment

Hatch manages virtual environments automatically. To create and enter a shell in the default dev environment:

```bash
hatch shell
```

To install pre-commit hooks (required before committing):

```bash
pip install pre-commit
pre-commit install
```

### Running tests

Run the full test matrix (all Python × Django version combinations defined in `pyproject.toml`):

```bash
hatch test -a
```

Run tests for a specific Python version only:

```bash
hatch test -i py=3.12
```

Run tests for a specific Python + Django combination:

```bash
hatch test -i py=3.12 -i django=5.2
```

Pass arguments through to pytest (e.g. run a single test file):

```bash
hatch test -- helsinki_health_endpoints/tests/test_views.py -v
```

### The test matrix

The matrix defined in `pyproject.toml` is:

| Python | Django |
|--------|--------|
| 3.10, 3.11 | 5.2 |
| 3.12, 3.13, 3.14 | 5.2, 6.0 |

Each combination gets its own isolated venv (created automatically by hatch on first run, stored in hatch's environment cache).

### Manual testing

The repository includes a `manage.py` pre-configured with the test settings (SQLite in-memory database). A dedicated `dev` Hatch environment sets the `DJANGO_SETTINGS_MODULE` for these test settings, which configure `DEBUG=True`:

```bash
hatch run dev:python manage.py runserver
```

Then hit the endpoints:

```bash
curl http://localhost:8000/healthz
curl http://localhost:8000/readiness
```

### Linting

```bash
# Run all pre-commit hooks against all files
pre-commit run --all-files

# Run only ruff lint (with autofix)
pre-commit run ruff-check --all-files

# Run only ruff formatter
pre-commit run ruff-format --all-files
```



## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
