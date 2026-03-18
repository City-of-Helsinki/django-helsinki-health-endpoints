import sys
from unittest.mock import patch

import pytest
from django.test import override_settings

from helsinki_health_endpoints.utils import _check_database, _get_package_version


@pytest.mark.skipif(
    sys.version_info >= (3, 11), reason="tomli fallback only applies on Python < 3.11"
)
class TestTomliImportFallback:
    def test_tomli_used_as_tomllib(self):
        """On Python < 3.11, tomli is imported as the tomllib fallback."""
        import helsinki_health_endpoints.utils as utils_module

        assert utils_module.tomllib.__name__ == "tomli"


class TestCheckDatabase:
    @pytest.mark.django_db
    def test_ok(self):
        assert _check_database() == "ok"

    def test_error_on_exception(self):
        with patch("helsinki_health_endpoints.utils.connection") as mock_conn:
            mock_conn.cursor.side_effect = Exception("DB is down")
            assert _check_database() == "error"


class TestGetPackageVersion:
    @pytest.fixture(autouse=True)
    def clear_cache(self):
        _get_package_version.cache_clear()
        yield
        _get_package_version.cache_clear()

    def test_reads_from_pyproject_toml(self, tmp_path):
        (tmp_path / "pyproject.toml").write_bytes(b'[project]\nversion = "3.2.1"\n')
        with override_settings(BASE_DIR=str(tmp_path)):
            assert _get_package_version() == "3.2.1"

    def test_returns_unknown_when_file_is_missing(self, tmp_path):
        with override_settings(BASE_DIR=str(tmp_path)):
            assert _get_package_version() == "unknown"

    def test_returns_unknown_when_version_key_absent(self, tmp_path):
        (tmp_path / "pyproject.toml").write_bytes(b"[project]\n")
        with override_settings(BASE_DIR=str(tmp_path)):
            assert _get_package_version() == "unknown"
