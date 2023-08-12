from django.urls import include, path

app_name = "api"


urlpatterns = [
    path("v1/", include(("api.v1.urls", "api"), namespace="v1")),
    # path("v3/", include(("api.v2.urls", "api"), namespace="v2")),
    # path("v2/", include(("api.v3.urls", "api"), namespace="v3")),
]
