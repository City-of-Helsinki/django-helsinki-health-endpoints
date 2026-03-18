from django.apps import AppConfig


class HelsinkiHealthEndpointsConfig(AppConfig):
    name = "helsinki_health_endpoints"
    verbose_name = "Health Endpoints"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        from . import checks  # noqa: F401 — registers Django system checks
