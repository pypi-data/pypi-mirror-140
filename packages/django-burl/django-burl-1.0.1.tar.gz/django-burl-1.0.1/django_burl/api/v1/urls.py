from rest_framework import routers
from django.urls import include, path

from django_burl.api.v1 import views, viewsets

router = routers.SimpleRouter()
router.register(r"redirects", viewsets.BriefURLViewSet, basename="redirect")


urlpatterns = [
    path("", views.api_root, name="redirects-root"),
    path("", include((router.urls, "redirects"))),
]
