from rest_framework import routers
from django.urls import include, path

from django_burl.api.v2 import views
from django_burl.api.v2 import viewsets

router = routers.SimpleRouter()
router.register(r"burls", viewsets.BriefURLViewSet, basename="burls")


urlpatterns = [
    path("", views.api_root, name="burls-root"),
    path("", include((router.urls, "burls"))),
]
