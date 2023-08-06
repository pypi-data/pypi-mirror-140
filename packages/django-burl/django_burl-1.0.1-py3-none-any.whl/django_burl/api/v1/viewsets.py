import uuid

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions

from django_burl.models import BriefURL
from django_burl.api.v1.serializers import BurlSerializer, BurlUserUUIDSerializer


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return obj.user == request.user


class BriefURLViewSet(ModelViewSet):
    permission_classes = (IsOwner, IsAuthenticated)
    filterset_fields = {
        "enabled": ["exact"],
        "description": ["exact", "icontains"],
        "created": ["exact", "lt", "gt", "lte", "gte"],
        "updated": ["exact", "lt", "gt", "lte", "gte"],
        "url": ["exact", "icontains"],
        "burl": ["exact", "icontains"],
    }
    lookup_field = "burl"

    def get_queryset(self):
        if self.request.user.is_superuser:
            return BriefURL.objects.order_by("-created")
        elif self.request.user.is_authenticated:
            return BriefURL.objects.filter(user=self.request.user).order_by("-created")
        else:
            return []

    def get_serializer_class(self):
        if type(self.request.user.id) == uuid.UUID:
            return BurlUserUUIDSerializer
        return BurlSerializer

    def perform_create(self, serializer):
        if (
            self.request.user.is_superuser
            and "user" in serializer._validated_data.keys()
        ):
            user = get_object_or_404(
                get_user_model(), id=serializer._validated_data["user"]["id"]
            )
            serializer.save(user=user)
        else:
            serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        if (
            self.request.user.is_superuser
            and "user" in serializer._validated_data.keys()
        ):
            user = get_object_or_404(
                get_user_model(), id=serializer._validated_data["user"]["id"]
            )
            serializer.save(user=user)
        else:
            serializer.save(user=self.request.user)
