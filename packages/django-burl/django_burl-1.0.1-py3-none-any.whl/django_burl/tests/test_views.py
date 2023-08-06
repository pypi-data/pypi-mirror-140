from django.contrib.sites.models import Site
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from django_burl.models import BriefURL


class BriefURLViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Site.objects.filter(id=1).update(domain="testserver")
        site = Site.objects.first()
        cls.user = get_user_model().objects.create_user("fry")
        cls.redirect = BriefURL.objects.create(
            user=cls.user, url="https://twitter.com", site=site
        )
        cls.redirect_disabled = BriefURL.objects.create(
            user=cls.user, url="https://google.com", enabled=False, site=site
        )

    def test_redirect(self):
        url = reverse("redirect", kwargs={"burl": self.redirect.burl})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.headers["location"], "https://twitter.com")

    def test_redirect_not_found(self):
        url = reverse("redirect", kwargs={"burl": "asdf1234"})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_redirect_disabled(self):
        url = reverse("redirect", kwargs={"burl": self.redirect_disabled.burl})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)
