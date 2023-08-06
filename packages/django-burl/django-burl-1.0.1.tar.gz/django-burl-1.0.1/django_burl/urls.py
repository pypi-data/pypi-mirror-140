from django.urls import include, path

from django_burl import views
from django_burl.api.v1 import urls as api_v1
from django_burl.api.v2 import urls as api_v2

app_name = "django_burl"

urlpatterns = [
    path("<str:burl>/", views.get_redirect, name="redirect"),
    path("api/v1/", include(api_v1)),
    path("api/v2/", include(api_v2)),
]
