from unittest.mock import patch

import pytest
from django.test import override_settings
from django.urls import reverse

from helsinki_health_endpoints.utils import _get_package_version


@pytest.fixture(autouse=True)
def clear_version_cache():
    _get_package_version.cache_clear()
    yield
    _get_package_version.cache_clear()


@pytest.fixture
def readiness_url():
    return reverse("helsinki_health_endpoints:readiness")


@pytest.fixture
def healthz_url():
    return reverse("helsinki_health_endpoints:healthz")


@pytest.mark.django_db
def test_readiness_ok(client, readiness_url):
    response = client.get(readiness_url)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "ok"
    assert {
        "status",
        "database",
        "packageVersion",
        "release",
    } == set(data)


@pytest.mark.django_db
def test_readiness_503_when_db_down(client, readiness_url):
    with patch("helsinki_health_endpoints.views._check_database", return_value="error"):
        response = client.get(readiness_url)

    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "error"
    assert data["database"] == "error"


def test_readiness_method_not_allowed_for_non_get(client, readiness_url):
    assert client.post(readiness_url).status_code == 405


@pytest.mark.django_db
@pytest.mark.parametrize(
    "release, expected",
    [(None, ""), ("app@v1.2.3", "app@v1.2.3")],
)
def test_readiness_sentry_release(client, readiness_url, release, expected):
    with override_settings(SENTRY_RELEASE=release):
        response = client.get(readiness_url)

    assert response.json()["release"] == expected


@pytest.mark.django_db
def test_healthz_returns_200(client, healthz_url):
    response = client.get(healthz_url)
    assert response.status_code == 200


def test_healthz_rejects_post(client, healthz_url):
    response = client.post(healthz_url)
    assert response.status_code == 405
