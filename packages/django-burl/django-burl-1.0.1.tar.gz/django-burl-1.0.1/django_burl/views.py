import logging

from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404

from django_burl.models import BriefURL


logger = logging.getLogger(__name__)


def get_redirect(request, burl):
    site = get_current_site(request)
    redirect = get_object_or_404(BriefURL, burl=burl, site=site, enabled=True)
    return HttpResponseRedirect(redirect.url)
