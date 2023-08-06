import uuid

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied, APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions

from django_burl.models import BriefURL, BriefURLDomainUser
from django_burl.api.v2.serializers import BurlSerializer, BurlUserUUIDSerializer


class ConflictException(APIException):
    status_code = 409
    default_detail = "your request conflicts with existing data"
    default_code = "resource_conflict"


class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        try:
            domain_user = BriefURLDomainUser.objects.get(
                user=request.user, site=request.site
            )
            if domain_user.is_creator:
                return True
        except (ObjectDoesNotExist, TypeError):
            return False
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        try:
            domain_user = BriefURLDomainUser.objects.get(
                user=request.user, site=request.site
            )
            if (
                domain_user.is_creator
                and obj.user == request.user
                and obj.site == request.site
            ):
                return True
            elif domain_user.is_editor and obj.site == request.site:
                return True
        except ObjectDoesNotExist:
            return False
        return False


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
            return BriefURL.objects.filter(site=self.request.site).order_by("-created")
        elif self.request.user.is_authenticated:
            try:
                domain_user = BriefURLDomainUser.objects.get(
                    user=self.request.user, site=self.request.site
                )
                if domain_user.is_editor:
                    return BriefURL.objects.filter(site=self.request.site).order_by(
                        "-created"
                    )
                elif domain_user.is_creator:
                    return BriefURL.objects.filter(
                        user=self.request.user, site=self.request.site
                    ).order_by("-created")
            except ObjectDoesNotExist:
                return BriefURL.objects.none()
        return BriefURL.objects.none()

    def get_serializer_class(self):
        if type(self.request.user.id) == uuid.UUID:
            return BurlUserUUIDSerializer
        return BurlSerializer

    def perform_create(self, serializer):
        if "user" in serializer.validated_data.keys():
            if self.request.user.is_superuser:
                user = get_object_or_404(
                    get_user_model(), id=serializer.validated_data["user"]["id"]
                )
                return self._save_with_integrity(serializer, user)
            else:
                raise PermissionDenied(
                    {"error": "must be superuser to create burl as another user"}
                )
        else:
            return self._save_with_integrity(serializer, self.request.user)

    def perform_destroy(self, instance):
        if self.request.user.is_superuser or self.request.user == instance.user:
            return instance.delete()
        else:
            try:
                domain_user = BriefURLDomainUser.objects.get(
                    user=self.request.user, site=self.request.site
                )
                if domain_user.is_admin:
                    return instance.delete()
            except ObjectDoesNotExist:
                pass
        raise PermissionDenied(
            {"error": "must be superuser or domain admin to delete other user's burl"}
        )

    def perform_update(self, serializer):
        if "user" in serializer.validated_data.keys():
            if serializer.validated_data["user"]["id"] != serializer.instance.user.id:
                if self.request.user.is_superuser:
                    user = get_object_or_404(
                        get_user_model(), id=serializer.validated_data["user"]["id"]
                    )
                    return self._save_with_integrity(serializer, user)
                else:
                    raise PermissionDenied(
                        {"error": "must be superuser to change burl user"}
                    )
            else:
                return self._save_with_integrity(serializer, serializer.instance.user)
        else:
            return self._save_with_integrity(serializer, serializer.instance.user)

    def _save_with_integrity(self, serializer, user):
        try:
            return serializer.save(user=user, site=self.request.site)
        except IntegrityError:
            raise ConflictException(
                {
                    "error": "burl already exists",
                    "burl": serializer.validated_data["burl"],
                }
            )
