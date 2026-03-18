from django.urls import include, path

urlpatterns = [
    path("", include("helsinki_health_endpoints.urls")),
]
