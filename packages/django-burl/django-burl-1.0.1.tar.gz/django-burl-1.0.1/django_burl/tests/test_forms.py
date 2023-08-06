from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.test import TestCase

from django_burl import utils
from django_burl.models import BriefURL
from django_burl.admin import BriefURLSuperForm


class BriefURLAdminFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        zoid = get_user_model().objects.create_user("zoidberg")
        site = Site.objects.first()
        cls.user = zoid
        cls.site = site
        cls.redirect = BriefURL.objects.create(
            user=zoid, url="https://google.com", site=site
        )

    def test_init(self):
        BriefURLSuperForm(self.redirect)

    def test_blacklisted_burl(self):
        redirect = self.redirect.__dict__
        redirect["burl"] = "admin"
        form = BriefURLSuperForm(redirect)
        self.assertTrue("burl" in form.errors)
        self.assertFalse(form.is_valid())

    def test_valid_burl(self):
        redirect = self.redirect.__dict__
        redirect["burl"] = utils.make_burl(1000)
        redirect["url"] = "https://google.com"
        redirect["user"] = self.user.id
        redirect["site"] = self.site
        form = BriefURLSuperForm(redirect)
        self.assertTrue(form.is_valid())
