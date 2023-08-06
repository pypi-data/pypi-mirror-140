from django.contrib.sites.models import Site
from django.db.models.manager import BaseManager
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.conf import settings

from django_burl import utils
from django_burl.database import RoughCountQuerySet


class BriefURLManager(BaseManager.from_queryset(RoughCountQuerySet)):
    pass


class BriefURL(models.Model):
    id = models.BigAutoField(primary_key=True)
    url = models.URLField(max_length=2048, db_index=True, verbose_name="URL")
    burl = models.CharField(
        max_length=2048,
        blank=True,
        db_index=True,
        verbose_name="Brief URL",
    )
    description = models.CharField(
        max_length=255, blank=True, help_text="description of the destination URL"
    )
    user = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)
    site = models.ForeignKey(Site, on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    enabled = models.BooleanField(default=True, db_index=True)
    objects = BriefURLManager()

    def __str__(self):
        return f"{self.site.domain}/{self.burl} → {self.url}"

    class Meta:
        unique_together = [["burl", "site"]]
        indexes = [
            models.Index(
                fields=["burl", "site", "enabled"],
                name="django_burl_briefurl_brl_st_on",
            ),
            models.Index(
                fields=["user", "site"], name="django_burl_briefurl_user_site"
            ),
        ]

    def _set_burl(self):
        if self.burl:
            self.random = False
            if self.burl in settings.BURL_BLACKLIST:
                raise ValidationError(
                    f'burl "{self.burl}" is blacklisted by BURL_BLACKLIST setting'
                )
        else:
            self.random = True
            self.burl = utils.make_burl(ceiling=BriefURL.objects.rough_count())
            if self.burl in settings.BURL_BLACKLIST:
                self.burl = None
                return self._set_burl()

    def save(self, *args, **kwargs):
        self._set_burl()
        try:
            with transaction.atomic():
                return super().save(*args, **kwargs)
        except IntegrityError as ex:
            if "unique constraint" in repr(ex):
                if self.random:
                    self.burl = None
                    return self.save(*args, **kwargs)
                else:
                    raise ex


class BriefURLDomainUser(models.Model):
    class Role(models.TextChoices):
        CREATOR = "creator"
        EDITOR = "editor"
        ADMIN = "admin"

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    role = models.CharField(max_length=16, choices=Role.choices, default=Role.CREATOR)

    def __str__(self):
        return f"@{self.user.username}: {self.role} on {self.site.domain}"

    class Meta:
        unique_together = [["site", "user"]]

    @property
    def is_creator(self):
        return self.role in [self.Role.CREATOR, self.Role.EDITOR, self.Role.ADMIN]

    @property
    def is_editor(self):
        return self.role in [self.Role.EDITOR, self.Role.ADMIN]

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN


class BriefURLDefaultRedirect(models.Model):
    id = models.AutoField(primary_key=True)
    site = models.OneToOneField(
        Site, on_delete=models.CASCADE, verbose_name="site", unique=True
    )
    url = models.URLField(verbose_name="redirect to")

    def __str__(self):
        return f"{self.site.domain} -> {self.url}"
