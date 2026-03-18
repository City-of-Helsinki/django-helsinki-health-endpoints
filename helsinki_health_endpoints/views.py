from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET

from .utils import _check_database, _get_package_version


@require_GET
def healthz(request):
    """Kubernetes liveness probe — always returns 200."""
    return HttpResponse(status=200)


@require_GET
def readiness(request):
    """Kubernetes readiness probe — returns app version, DB status, and build info."""
    db_status = _check_database()
    readiness_status = 200 if db_status == "ok" else 503
    release = getattr(settings, "SENTRY_RELEASE", None) or ""

    return JsonResponse(
        {
            "status": db_status,
            "packageVersion": _get_package_version(),
            "release": release,
            "database": db_status,
        },
        status=readiness_status,
    )
