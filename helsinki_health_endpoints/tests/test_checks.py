from unittest.mock import patch

from django.test import override_settings

from helsinki_health_endpoints.checks import (
    _pyproject_excluded_by_dockerignore,
    check_base_dir,
    check_pyproject_not_dockerignored,
)


class TestCheckBaseDir:
    def test_ok(self):
        assert check_base_dir(app_configs=None) == []

    @override_settings()
    def test_missing(self):
        from django.conf import settings

        del settings.BASE_DIR
        errors = check_base_dir(app_configs=None)
        assert len(errors) == 1
        assert errors[0].id == "helsinki_health_endpoints.E001"


class TestPyprojectExcludedByDockerignore:
    def test_no_matching_pattern(self):
        assert (
            _pyproject_excluded_by_dockerignore(["node_modules/", "dist/", "*.log"])
            is None
        )

    def test_exact_match(self):
        assert (
            _pyproject_excluded_by_dockerignore(["node_modules/", "pyproject.toml"])
            == "pyproject.toml"
        )

    def test_toml_glob(self):
        assert _pyproject_excluded_by_dockerignore(["*.toml"]) == "*.toml"

    def test_negation_overrides_exclusion(self):
        assert (
            _pyproject_excluded_by_dockerignore(["*.toml", "!pyproject.toml"]) is None
        )

    def test_comment_lines_ignored(self):
        assert (
            _pyproject_excluded_by_dockerignore(["# pyproject.toml", "*.log"]) is None
        )

    def test_leading_slash_exact_match(self):
        assert (
            _pyproject_excluded_by_dockerignore(["/pyproject.toml"])
            == "/pyproject.toml"
        )

    def test_double_star_glob(self):
        assert (
            _pyproject_excluded_by_dockerignore(["**/pyproject.toml"])
            == "**/pyproject.toml"
        )

    def test_leading_slash_negation_overrides_exclusion(self):
        assert (
            _pyproject_excluded_by_dockerignore(["*.toml", "!/pyproject.toml"]) is None
        )


class TestCheckPyprojectNotDockerignored:
    def test_no_dockerignore(self, tmp_path):
        with override_settings(BASE_DIR=str(tmp_path)):
            assert check_pyproject_not_dockerignored(app_configs=None) == []

    def test_clean_dockerignore(self, tmp_path):
        (tmp_path / ".dockerignore").write_text("node_modules/\n*.log\n")
        with override_settings(BASE_DIR=str(tmp_path)):
            assert check_pyproject_not_dockerignored(app_configs=None) == []

    def test_pyproject_excluded(self, tmp_path):
        (tmp_path / ".dockerignore").write_text("*.toml\n")
        with override_settings(BASE_DIR=str(tmp_path)):
            errors = check_pyproject_not_dockerignored(app_configs=None)
        assert len(errors) == 1
        assert errors[0].id == "helsinki_health_endpoints.E002"
        assert "*.toml" in errors[0].msg

    def test_negation_overrides_exclusion(self, tmp_path):
        (tmp_path / ".dockerignore").write_text("*.toml\n!pyproject.toml\n")
        with override_settings(BASE_DIR=str(tmp_path)):
            assert check_pyproject_not_dockerignored(app_configs=None) == []

    def test_oserror_on_read_returns_warning(self, tmp_path):
        (tmp_path / ".dockerignore").write_text("*.toml\n")
        with (
            override_settings(BASE_DIR=str(tmp_path)),
            patch("pathlib.Path.read_text", side_effect=OSError("permission denied")),
        ):
            warnings = check_pyproject_not_dockerignored(app_configs=None)
        assert len(warnings) == 1
        assert warnings[0].id == "helsinki_health_endpoints.W001"
        assert "permission denied" in warnings[0].msg

    @override_settings()
    def test_skips_when_no_base_dir(self):
        from django.conf import settings

        del settings.BASE_DIR
        assert check_pyproject_not_dockerignored(app_configs=None) == []
