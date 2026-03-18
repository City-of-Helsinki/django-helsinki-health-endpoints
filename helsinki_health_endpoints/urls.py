from django.urls import path

from . import views

app_name = "helsinki_health_endpoints"

urlpatterns = [
    path("healthz", views.healthz, name="healthz"),
    path("readiness", views.readiness, name="readiness"),
]
