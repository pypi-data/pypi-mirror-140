from django.contrib import admin
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.utils.translation import gettext as _
from django.conf import settings
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from django_burl.models import BriefURL, BriefURLDomainUser, BriefURLDefaultRedirect


class BriefURLMixin:
    class Meta:
        model = BriefURL
        fields = "__all__"

    def clean_burl(self):
        burl = self.cleaned_data["burl"]
        if burl in settings.BURL_BLACKLIST:
            raise ValidationError(
                _("The specified brief URL is blacklisted and cannot be used!")
            )
        return burl


class BriefURLSuperForm(forms.ModelForm, BriefURLMixin):
    user = forms.ModelChoiceField(get_user_model().objects.all(), required=True)
    site = forms.ModelChoiceField(Site.objects.all(), required=True)


class BriefUrlEditorForm(forms.ModelForm, BriefURLMixin):
    user = forms.ModelChoiceField(
        get_user_model().objects.all(), disabled=True, required=True
    )
    site = forms.ModelChoiceField(Site.objects.all(), disabled=True, required=True)


class BriefURLAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        if request.user.is_superuser:
            form = BriefURLSuperForm
        else:
            form = BriefUrlEditorForm
        form.base_fields["user"].initial = request.user
        form.base_fields["site"].initial = request.site
        return form

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        try:
            domain_user = BriefURLDomainUser.objects.get(
                user=request.user, site=request.site
            )
            if domain_user.is_editor:
                return super().get_queryset(request).filter(site=request.site)
            elif domain_user.is_creator:
                return (
                    super()
                    .get_queryset(request)
                    .filter(site=request.site, user=request.user)
                )
            else:
                return BriefURL.objects.none()
        except ObjectDoesNotExist:
            return BriefURL.objects.none()

    def has_add_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        try:
            domain_user = BriefURLDomainUser.objects.get(
                user=request.user, site=request.site
            )
            if domain_user.is_creator:
                return True
        except ObjectDoesNotExist:
            return False
        return False

    def has_change_permission(self, request, obj=None):
        return self._domain_user_owner(request, obj)

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        try:
            domain_user = BriefURLDomainUser.objects.get(
                user=request.user, site=request.site
            )
            if domain_user.is_admin:
                return True
            if domain_user.is_creator:
                if obj and obj.user == request.user:
                    return True
                elif not obj:
                    return True
        except ObjectDoesNotExist:
            return False
        return False

    def has_view_permission(self, request, obj=None):
        return self._domain_user_owner(request, obj)

    def _domain_user_owner(self, request, obj):
        if request.user.is_superuser:
            return True
        try:
            domain_user = BriefURLDomainUser.objects.get(
                user=request.user, site=request.site
            )
            if domain_user.is_editor:
                return True
            if domain_user.is_creator:
                if obj and obj.user == request.user:
                    return True
                elif not obj:
                    return True
        except ObjectDoesNotExist:
            return False
        return False


class BriefURLDefaultRedirectMixin:
    class Meta:
        model = BriefURLDefaultRedirect
        fields = "__all__"


class BriefURLDefaultRedirectSuperForm(forms.ModelForm, BriefURLDefaultRedirectMixin):
    pass


class BriefURLDefaultRedirectEditorForm(forms.ModelForm, BriefURLDefaultRedirectMixin):
    site = forms.ModelChoiceField(Site.objects.all(), disabled=True)


class BriefURLDefaultRedirectAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        if request.user.is_superuser:
            form = BriefURLDefaultRedirectSuperForm
        else:
            form = BriefURLDefaultRedirectEditorForm
        form.base_fields["site"].initial = request.site
        return form

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        try:
            domain_user = BriefURLDomainUser.objects.get(
                user=request.user, site=request.site
            )
            if domain_user.is_admin:
                return super().get_queryset(request).filter(site=request.site)
            else:
                return super().get_queryset(request).none()
        except ObjectDoesNotExist:
            return super().get_queryset(request).none()

    def has_view_permission(self, request, **_kwargs):
        return self._super_or_domain_admin(request)

    def has_change_permission(self, request, **_kwargs):
        return self._super_or_domain_admin(request)

    def has_add_permission(self, request, **_kwargs):
        return self._super_or_domain_admin(request)

    def has_delete_permission(self, request, **_kwargs):
        return self._super_or_domain_admin(request)

    def _super_or_domain_admin(self, request):
        if request.user.is_superuser:
            return True
        try:
            domain_user = BriefURLDomainUser.objects.get(
                user=request.user, site=request.site
            )
            if domain_user.is_admin:
                return True
        except ObjectDoesNotExist:
            return False
        return False


admin.site.register(BriefURL, BriefURLAdmin)
admin.site.register(BriefURLDomainUser)
admin.site.register(BriefURLDefaultRedirect, BriefURLDefaultRedirectAdmin)
