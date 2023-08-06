from datetime import datetime

from django.contrib.sites.models import Site
from django.db import connection, IntegrityError
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.conf import settings

from django_burl.models import BriefURL, BriefURLDomainUser


class BriefURLModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user("leela")
        cls.url = "https://google.com"
        cls.description = "test redirect"
        cls.site = Site.objects.first()

    def test_create_redirect_random_burl(self):
        redirect = BriefURL.objects.create(
            url=self.url, description=self.description, user=self.user
        )
        self.assertIsInstance(redirect, BriefURL)
        self.assertEquals(redirect.url, "https://google.com")
        self.assertIsInstance(redirect.burl, str)
        self.assertEquals(redirect.description, "test redirect")
        self.assertIsInstance(redirect.created, datetime)
        self.assertIsInstance(redirect.created, datetime)
        self.assertTrue(redirect.enabled)

    def test_create_redirect_custom_burl(self):
        redirect = BriefURL.objects.create(
            url=self.url, description=self.description, user=self.user, burl="google"
        )
        self.assertIsInstance(redirect, BriefURL)
        self.assertEquals(redirect.url, "https://google.com")
        self.assertEquals(redirect.burl, "google")
        self.assertEquals(redirect.description, "test redirect")
        self.assertIsInstance(redirect.created, datetime)
        self.assertIsInstance(redirect.created, datetime)
        self.assertTrue(redirect.enabled)

    def test_create_redirect_custom_blacklisted_burl(self):
        with self.assertRaises(ValidationError):
            BriefURL.objects.create(user=self.user, url=self.url, burl="admin")

    def test_create_redirect_custom_duplicate_burl(self):
        BriefURL.objects.create(
            url=self.url, user=self.user, burl="test_duplicate", site=self.site
        )
        with self.assertRaises(IntegrityError):
            BriefURL.objects.create(
                url=self.url, user=self.user, burl="test_duplicate", site=self.site
            )


class BriefURLManagerTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        if connection.vendor == "postgresql":
            cls.min = settings.ROUGH_COUNT_MIN - 100
            cls.max = settings.ROUGH_COUNT_MIN * 2
            cls.user = get_user_model().objects.create_user("hermes")
            cls.url = "https://google.com"
            cls.site = Site.objects.first()
            count = 0
            while count < cls.min:
                BriefURL.objects.create(user=cls.user, url=cls.url)
                count += 1

    def test_rough_count_under_min(self):
        if connection.vendor == "postgresql":
            self.assertIsInstance(BriefURL.objects.count(), int)
            self.assertIsInstance(BriefURL.objects.rough_count(), int)
            self.assertEquals(BriefURL.objects.count(), BriefURL.objects.rough_count())

    def test_rough_count_over_min(self):
        if connection.vendor == "postgresql":
            count = BriefURL.objects.count()
            while self.max - count > 0:
                BriefURL.objects.create(user=self.user, url=self.url, site=self.site)
                count += 1
            count = BriefURL.objects.count()
            rough_count = BriefURL.objects.rough_count()
            self.assertIsInstance(count, int)
            self.assertIsInstance(rough_count, int)
            self.assertTrue(abs(count - rough_count) < count * 0.5)


class BriefURLDomainUserTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fry = get_user_model().objects.create_user("fry")
        cls.amy = get_user_model().objects.create_user("amy")
        cls.leela = get_user_model().objects.create_user("leela")
        cls.url = "https://google.com"
        cls.description = "test redirect"
        cls.site = Site.objects.first()
        cls.fry_user_domain = BriefURLDomainUser.objects.create(
            site=cls.site, user=cls.fry, role=BriefURLDomainUser.Role.CREATOR
        )
        cls.amy_user_domain = BriefURLDomainUser.objects.create(
            site=cls.site, user=cls.amy, role=BriefURLDomainUser.Role.EDITOR
        )
        cls.leela_user_domain = BriefURLDomainUser.objects.create(
            site=cls.site, user=cls.leela, role=BriefURLDomainUser.Role.ADMIN
        )

    def test_is_creator(self):
        self.assertTrue(self.fry_user_domain.is_creator)
        self.assertTrue(self.amy_user_domain.is_creator)
        self.assertTrue(self.leela_user_domain.is_creator)

    def test_is_editor(self):
        self.assertFalse(self.fry_user_domain.is_editor)
        self.assertTrue(self.amy_user_domain.is_editor)
        self.assertTrue(self.leela_user_domain.is_editor)

    def test_is_admin(self):
        self.assertFalse(self.fry_user_domain.is_admin)
        self.assertFalse(self.amy_user_domain.is_admin)
        self.assertTrue(self.leela_user_domain.is_admin)
