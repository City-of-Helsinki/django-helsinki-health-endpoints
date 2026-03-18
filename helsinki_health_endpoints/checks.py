import fnmatch
from pathlib import Path

from django.conf import settings
from django.core.checks import Error, Warning, register


@register
def check_base_dir(app_configs, **kwargs):
    """Verify that BASE_DIR is defined in Django settings."""
    if not getattr(settings, "BASE_DIR", None):
        return [
            Error(
                "BASE_DIR is not defined in settings.",
                hint="""Add BASE_DIR to your Django settings pointing to the
                project root directory.""",
                id="helsinki_health_endpoints.E001",
            )
        ]
    return []


def _pyproject_excluded_by_dockerignore(lines: list[str]) -> str | None:
    """Return the matching pattern if pyproject.toml is excluded, otherwise None."""
    excluded = False
    matched_by = None
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        negate = stripped.startswith("!")
        raw_pattern = stripped[1:] if negate else stripped
        pattern = raw_pattern.lstrip("/")
        if pattern.startswith("**/"):
            pattern = pattern[3:]
        if fnmatch.fnmatch("pyproject.toml", pattern):
            excluded = not negate
            matched_by = None if negate else raw_pattern
    return matched_by if excluded else None


@register
def check_pyproject_not_dockerignored(app_configs, **kwargs):
    """Verify that pyproject.toml is not excluded by .dockerignore."""
    if not getattr(settings, "BASE_DIR", None):
        return []  # Already reported by check_base_dir

    dockerignore_path = Path(settings.BASE_DIR) / ".dockerignore"
    if not dockerignore_path.exists():
        return []

    try:
        lines = dockerignore_path.read_text(encoding="utf-8").splitlines()
    except OSError as e:
        return [
            Warning(
                f"Could not read .dockerignore: {e}",
                hint="Ensure .dockerignore is readable.",
                id="helsinki_health_endpoints.W001",
            )
        ]

    matched_by = _pyproject_excluded_by_dockerignore(lines)
    if matched_by:
        return [
            Error(
                f"pyproject.toml is excluded in .dockerignore (matched by '{matched_by}').",  # noqa: E501
                hint=(
                    "Remove the exclusion or add '!pyproject.toml' to .dockerignore. "
                    "The file is required at runtime to read the package version."
                ),
                id="helsinki_health_endpoints.E002",
            )
        ]
    return []
