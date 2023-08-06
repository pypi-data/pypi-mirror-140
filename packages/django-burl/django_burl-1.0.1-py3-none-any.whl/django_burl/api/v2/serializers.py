from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from django_burl.models import BriefURL


class BurlSerializerBase(serializers.ModelSerializer):
    class Meta:
        model = BriefURL
        fields = (
            "burl",
            "url",
            "user",
            "description",
            "enabled",
            "created",
            "updated",
        )

    def validate_burl(self, value):
        if value in settings.BURL_BLACKLIST:
            raise PermissionDenied(
                {"error": "blacklisted by BURL_BLACKLIST setting", "burl": value}
            )
        return value


class BurlSerializer(BurlSerializerBase):
    user = serializers.IntegerField(required=False, source="user.id")


class BurlUserUUIDSerializer(BurlSerializerBase):
    user = serializers.UUIDField(required=False, source="user.id")
