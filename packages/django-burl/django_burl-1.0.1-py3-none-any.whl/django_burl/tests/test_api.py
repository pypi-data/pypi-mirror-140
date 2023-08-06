from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.urls import reverse

from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from django_burl.models import BriefURL, BriefURLDomainUser


class BurlApiTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # update the first site to match the default domain used by the testing client
        Site.objects.filter(id=1).update(domain="testserver", name="testserver")
        cls.site = Site.objects.get(id=1)
        cls.site2 = Site.objects.create(domain="go.to", name="goto")
        cls.url = "https://en.wikipedia.org"
        cls.amy = get_user_model().objects.create_user("amy")
        cls.bender = get_user_model().objects.create_user("bender", is_superuser=True)
        cls.farnsworth = get_user_model().objects.create_user("farnsworth")
        cls.fry = get_user_model().objects.create_user("fry")
        cls.hermes = get_user_model().objects.create_user("hermes")
        cls.kif = get_user_model().objects.create_user("kif")
        cls.leela = get_user_model().objects.create_user("leela")
        cls.zoidberg = get_user_model().objects.create_user("zoidberg")
        Token.objects.create(user=cls.amy)
        Token.objects.create(user=cls.bender)
        Token.objects.create(user=cls.farnsworth)
        Token.objects.create(user=cls.fry)
        Token.objects.create(user=cls.hermes)
        Token.objects.create(user=cls.kif)
        Token.objects.create(user=cls.leela)
        Token.objects.create(user=cls.zoidberg)
        BriefURLDomainUser.objects.create(
            site=cls.site, user=cls.fry, role=BriefURLDomainUser.Role.CREATOR
        )
        BriefURLDomainUser.objects.create(
            site=cls.site, user=cls.amy, role=BriefURLDomainUser.Role.EDITOR
        )
        BriefURLDomainUser.objects.create(
            site=cls.site, user=cls.leela, role=BriefURLDomainUser.Role.ADMIN
        )
        BriefURLDomainUser.objects.create(
            site=cls.site2, user=cls.leela, role=BriefURLDomainUser.Role.CREATOR
        )
        BriefURLDomainUser.objects.create(
            site=cls.site2, user=cls.kif, role=BriefURLDomainUser.Role.EDITOR
        )
        BriefURLDomainUser.objects.create(
            site=cls.site2, user=cls.farnsworth, role=BriefURLDomainUser.Role.ADMIN
        )


class BurlCreateTests(BurlApiTestCase):
    def test_create_duplicate_same_domain(self):
        redirect = BriefURL.objects.create(
            user=self.fry, url=self.url, burl="moz", site=self.site
        )
        data = {"url": "https://www.mozilla.org", "burl": "moz"}
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.fry.auth_token.key}")
        response = self.client.post(reverse("burls:burls-list"), data, format="json")
        self.assertEquals(response.status_code, 409)
        redirect.refresh_from_db()
        self.assertEquals(redirect.url, self.url)

    def test_create_duplicate_different_domain(self):
        redirect = BriefURL.objects.create(
            user=self.farnsworth, url=self.url, burl="moz", site=self.site2
        )
        data = {"url": "https://www.mozilla.org", "burl": "moz"}
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.fry.auth_token.key}")
        response = self.client.post(reverse("burls:burls-list"), data, format="json")
        self.assertEquals(response.status_code, 201)
        redirect2 = BriefURL.objects.get(burl=response.json()["burl"], site=self.site)
        redirect.refresh_from_db()
        self.assertEquals(redirect.burl, "moz")
        self.assertEquals(redirect.user, self.farnsworth)
        self.assertEquals(redirect.url, self.url)
        self.assertEquals(redirect.site, self.site2)
        self.assertEquals(redirect2.burl, "moz")
        self.assertEquals(redirect2.user, self.fry)
        self.assertEquals(redirect2.url, "https://www.mozilla.org")
        self.assertEquals(redirect2.site, self.site)

    def test_create_random_unauthorized(self):
        data = {"url": "https://en.wikipedia.org", "user": self.kif.id}
        response = self.client.post(reverse("burls:burls-list"), data, format="json")
        self.assertEquals(response.status_code, 401)

    def test_create_random_no_domain_user(self):
        data = {"url": self.url, "user": self.zoidberg.id}
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.zoidberg.auth_token.key}"
        )
        response = self.client.post(reverse("burls:burls-list"), data, format="json")
        self.assertEquals(response.status_code, 403)

    def test_create_random_site1_burl_as_site2_user(self):
        data = {"url": self.url}
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.farnsworth.auth_token.key}"
        )
        response = self.client.post(
            reverse("burls:burls-list"),
            data,
            format="json",
        )
        self.assertEquals(response.status_code, 403)

    def test_create_random_as_creator(self):
        data = {"url": self.url, "description": "test1"}
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.fry.auth_token.key}")
        response = self.client.post(reverse("burls:burls-list"), data, format="json")
        self.assertEquals(response.status_code, 201)
        redirect = BriefURL.objects.get(burl=response.json()["burl"])
        self.assertEquals(redirect.user.id, self.fry.id)
        self.assertEquals(redirect.burl, response.json()["burl"])
        self.assertEquals(redirect.url, "https://en.wikipedia.org")
        self.assertEquals(redirect.description, "test1")
        self.assertTrue(redirect.enabled)

    def test_create_specific_as_creator(self):
        data = {"url": self.url, "description": "test", "burl": "burl_test_1"}
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.fry.auth_token.key}")
        response = self.client.post(reverse("burls:burls-list"), data, format="json")
        self.assertEquals(response.status_code, 201)
        redirect = BriefURL.objects.get(burl="burl_test_1")
        self.assertEquals(redirect.user.id, self.fry.id)
        self.assertEquals(redirect.burl, "burl_test_1")
        self.assertEquals(redirect.url, "https://en.wikipedia.org")
        self.assertEquals(redirect.description, "test")
        self.assertTrue(redirect.enabled)

    def test_create_random_for_other_user_as_creator(self):
        data = {"url": "https://en.wikipedia.org", "user": self.amy.id}
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.fry.auth_token.key}")
        response = self.client.post(reverse("burls:burls-list"), data, format="json")
        self.assertEquals(response.status_code, 403)
        self.assertEquals(
            str(response.json()["error"]),
            "must be superuser to create burl as another user",
        )

    def test_create_random_for_other_user_as_editor(self):
        data = {"url": "https://en.wikipedia.org", "user": self.fry.id}
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.amy.auth_token.key}")
        response = self.client.post(reverse("burls:burls-list"), data, format="json")
        self.assertEquals(response.status_code, 403)
        self.assertEquals(
            str(response.json()["error"]),
            "must be superuser to create burl as another user",
        )

    def test_create_random_for_other_user_as_superuser(self):
        data = {"url": "https://en.wikipedia.org", "user": self.leela.id}
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.bender.auth_token.key}"
        )
        response = self.client.post(reverse("burls:burls-list"), data, format="json")
        self.assertEquals(response.status_code, 201)
        self.assertEquals(str(response.json()["user"]), str(self.leela.id))

    def test_create_random_as_superuser(self):
        data = {
            "url": self.url,
            "description": "test1",
            "burl": "burl_test_1",
        }
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.bender.auth_token.key}"
        )
        response = self.client.post(reverse("burls:burls-list"), data, format="json")
        self.assertEquals(response.status_code, 201)
        self.assertEquals(response.json()["user"], self.bender.id)

    def test_create_blacklisted_as_creator(self):
        data = {"url": self.url, "description": "test1", "burl": "admin"}
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.fry.auth_token.key}")
        response = self.client.post(reverse("burls:burls-list"), data, format="json")
        self.assertEquals(response.status_code, 403)


class BurlReadTests(BurlApiTestCase):
    def test_detail_no_domain(self):
        redirect = BriefURL.objects.create(user=self.fry, url=self.url, site=self.site)
        url = reverse("burls:burls-detail", kwargs={"burl": redirect.burl})
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.zoidberg.auth_token.key}"
        )
        response = self.client.get(url)
        self.assertEquals(response.status_code, 403)

    def test_detail_owned_by_creator_as_creator(self):
        redirect = BriefURL.objects.create(
            user=self.fry, url=self.url, description="hello, world!", site=self.site
        )
        url = reverse("burls:burls-detail", kwargs={"burl": redirect.burl})
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.fry.auth_token.key}")
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(redirect.burl, response.json()["burl"])
        self.assertEquals(str(redirect.user.id), str(response.json()["user"]))
        self.assertEquals(redirect.description, response.json()["description"])
        self.assertEquals(redirect.url, response.json()["url"])

    def test_detail_owned_by_creator_as_editor(self):
        redirect = BriefURL.objects.create(
            user=self.fry, url=self.url, description="hello, world!", site=self.site
        )
        url = reverse("burls:burls-detail", kwargs={"burl": redirect.burl})
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.amy.auth_token.key}")
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(str(redirect.user.id), str(response.json()["user"]))

    def test_detail_owned_by_editor_as_superuser(self):
        redirect = BriefURL.objects.create(user=self.amy, url=self.url, site=self.site)
        url = reverse("burls:burls-detail", kwargs={"burl": redirect.burl})
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.bender.auth_token.key}"
        )
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(str(response.json()["user"]), str(redirect.user.id))

    def test_detail_owned_by_other_user_as_creator(self):
        redirect = BriefURL.objects.create(user=self.amy, url=self.url, site=self.site)
        url = reverse("burls:burls-detail", kwargs={"burl": redirect.burl})
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.fry.auth_token.key}")
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_detail_owned_by_admin_as_editor(self):
        redirect = BriefURL.objects.create(
            user=self.leela, url=self.url, site=self.site
        )
        url = reverse("burls:burls-detail", kwargs={"burl": redirect.burl})
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.amy.auth_token.key}")
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.json()["user"], self.leela.id)

    def test_detail_site2_burl_as_site1_user(self):
        redirect = BriefURL.objects.create(user=self.kif, url=self.url, site=self.site2)
        url = reverse("burls:burls-detail", kwargs={"burl": redirect.burl})
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.amy.auth_token.key}")
        response = self.client.get(url, SERVER_NAME=self.site2.domain)
        self.assertEquals(response.status_code, 403)

    def test_detail_unauthorized(self):
        redirect = BriefURL.objects.create(user=self.amy, url=self.url, site=self.site)
        url = reverse("burls:burls-detail", kwargs={"burl": redirect.burl})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 401)

    def test_list_as_creator(self):
        BriefURL.objects.create(user=self.fry, url=self.url, site=self.site)
        BriefURL.objects.create(user=self.leela, url=self.url, site=self.site)
        url = reverse("burls:burls-list")
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.fry.auth_token.key}")
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.json()["results"]), 1)
        self.assertEquals(str(response.json()["results"][0]["user"]), str(self.fry.id))

    def test_list_as_editor(self):
        BriefURL.objects.create(user=self.fry, url=self.url, site=self.site)
        BriefURL.objects.create(user=self.leela, url=self.url, site=self.site)
        url = reverse("burls:burls-list")
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.amy.auth_token.key}")
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.json()["results"]), 2)
        users = [str(result["user"]) for result in response.json()["results"]]
        self.assertIn(str(self.fry.id), users)
        self.assertIn(str(self.leela.id), users)

    def test_list_as_superuser(self):
        BriefURL.objects.create(user=self.fry, url=self.url, site=self.site)
        BriefURL.objects.create(user=self.leela, url=self.url, site=self.site)
        url = reverse("burls:burls-list")
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.bender.auth_token.key}"
        )
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.json()["results"]), 2)
        users = [str(result["user"]) for result in response.json()["results"]]
        self.assertIn(str(self.fry.id), users)
        self.assertIn(str(self.leela.id), users)

    def test_list_no_domain(self):
        BriefURL.objects.create(user=self.fry, url=self.url, site=self.site)
        url = reverse("burls:burls-list")
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.zoidberg.auth_token.key}"
        )
        response = self.client.get(url)
        self.assertEquals(response.status_code, 403)

    def test_list_site2_as_site1_user(self):
        BriefURL.objects.create(user=self.leela, url=self.url, site=self.site2)
        BriefURL.objects.create(user=self.kif, url=self.url, site=self.site2)
        url = reverse("burls:burls-list")
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.amy.auth_token.key}")
        response = self.client.get(url, SERVER_NAME=self.site2.domain)
        self.assertEquals(response.status_code, 403)

    def test_list_unauthorized(self):
        BriefURL.objects.create(user=self.amy, url=self.url, site=self.site)
        url = reverse("burls:burls-list")
        response = self.client.get(url)
        self.assertEquals(response.status_code, 401)


class BurlUpdateTests(BurlApiTestCase):
    def test_update_change_user_as_non_superuser(self):
        redirect = BriefURL.objects.create(user=self.fry, url=self.url, site=self.site)
        data = {
            "url": "https://facebook.com",
            "description": "friendface",
            "burl": "zuck",
            "user": self.leela.id,
        }
        url = reverse("burls:burls-detail", kwargs={"burl": redirect.burl})
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.amy.auth_token.key}")
        response = self.client.put(url, data, format="json")
        self.assertEquals(response.status_code, 403)

    def test_update_change_user_as_superuser(self):
        burl = BriefURL.objects.create(user=self.leela, url=self.url, site=self.site)
        data = {"url": "https://facebook.com", "user": self.fry.id}
        url = reverse("burls:burls-detail", kwargs={"burl": burl.burl})
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.bender.auth_token.key}"
        )
        response = self.client.patch(url, data, format="json")
        self.assertEquals(response.status_code, 200)
        burl.refresh_from_db()
        self.assertEquals(burl.url, "https://facebook.com")
        self.assertEquals(burl.user, self.fry)

    def test_update_patch_by_admin_as_creator(self):
        redirect = BriefURL.objects.create(
            user=self.leela, url=self.url, site=self.site, description="leela's link"
        )
        data = {"url": "https://www.mozilla.org"}
        url = reverse("burls:burls-detail", kwargs={"burl": redirect.burl})
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.fry.auth_token.key}")
        response = self.client.patch(url, data, format="json")
        self.assertEquals(response.status_code, 404)

    def test_update_patch_by_admin_as_editor(self):
        redirect = BriefURL.objects.create(
            user=self.leela, url=self.url, site=self.site, description="leela's link"
        )
        start_burl = redirect.burl
        data = {"url": "https://www.mozilla.org"}
        url = reverse("burls:burls-detail", kwargs={"burl": redirect.burl})
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.amy.auth_token.key}")
        response = self.client.patch(url, data, format="json")
        self.assertEquals(response.status_code, 200)
        redirect.refresh_from_db()
        self.assertEquals(redirect.burl, start_burl)
        self.assertEquals(redirect.description, "leela's link")
        self.assertEquals(redirect.url, "https://www.mozilla.org")
        self.assertEquals(redirect.user, self.leela)

    def test_update_patch_by_creator_as_creator(self):
        redirect = BriefURL.objects.create(
            user=self.fry, url=self.url, site=self.site, description="fry's link"
        )
        start_burl = redirect.burl
        data = {
            "url": "https://twitter.com",
        }
        url = reverse("burls:burls-detail", kwargs={"burl": redirect.burl})
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.fry.auth_token.key}")
        response = self.client.patch(url, data, format="json")
        self.assertEquals(response.status_code, 200)
        redirect.refresh_from_db()
        self.assertEquals(redirect.burl, start_burl)
        self.assertEquals(redirect.description, "fry's link")
        self.assertEquals(redirect.url, "https://twitter.com")
        self.assertEquals(redirect.user, self.fry)

    def test_update_patch_by_creator_as_editor(self):
        burl = BriefURL.objects.create(user=self.fry, url=self.url, site=self.site)
        data = {"url": "https://facebook.com"}
        url = reverse("burls:burls-detail", kwargs={"burl": burl.burl})
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.amy.auth_token.key}")
        response = self.client.patch(url, data, format="json")
        self.assertEquals(response.status_code, 200)
        burl.refresh_from_db()
        self.assertEquals(burl.url, "https://facebook.com")

    def test_update_patch_no_domain(self):
        redirect = BriefURL.objects.create(user=self.kif, url=self.url, site=self.site)
        data = {
            "description": "friendface",
        }
        url = reverse("burls:burls-detail", kwargs={"burl": redirect.burl})
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.zoidberg.auth_token.key}"
        )
        response = self.client.patch(url, data, format="json")
        self.assertEquals(response.status_code, 403)

    def test_update_patch_unauthorized(self):
        redirect = BriefURL.objects.create(user=self.kif, url=self.url, site=self.site)
        data = {
            "description": "friendface",
        }
        url = reverse("burls:burls-detail", kwargs={"burl": redirect.burl})
        response = self.client.patch(url, data, format="json")
        self.assertEquals(response.status_code, 401)

    def test_update_put_by_creator_as_creator(self):
        redirect = BriefURL.objects.create(
            user=self.fry, url=self.url, site=self.site, description="fry's link"
        )
        data = {
            "url": "https://twitter.com",
            "description": "twitter",
            "burl": "twitter",
        }
        url = reverse("burls:burls-detail", kwargs={"burl": redirect.burl})
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.fry.auth_token.key}")
        response = self.client.put(url, data, format="json")
        self.assertEquals(response.status_code, 200)
        redirect.refresh_from_db()
        self.assertEquals(redirect.burl, "twitter")
        self.assertEquals(redirect.description, "twitter")
        self.assertEquals(redirect.url, "https://twitter.com")
        self.assertEquals(redirect.user, self.fry)

    def test_update_put_by_creator_as_editor(self):
        redirect = BriefURL.objects.create(
            user=self.fry, url=self.url, site=self.site, description="fry's link"
        )
        data = {
            "url": "https://www.mozilla.org",
            "description": "mozilla",
            "burl": "moz",
        }
        url = reverse("burls:burls-detail", kwargs={"burl": redirect.burl})
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.amy.auth_token.key}")
        response = self.client.put(url, data, format="json")
        self.assertEquals(response.status_code, 200)
        redirect.refresh_from_db()
        self.assertEquals(redirect.burl, "moz")
        self.assertEquals(redirect.description, "mozilla")
        self.assertEquals(redirect.url, "https://www.mozilla.org")
        self.assertEquals(redirect.user, self.fry)

    def test_update_put_no_domain(self):
        redirect = BriefURL.objects.create(user=self.kif, url=self.url, site=self.site)
        data = {
            "url": "https://www.mozilla.org",
            "description": "friendface",
            "burl": "moz",
        }
        url = reverse("burls:burls-detail", kwargs={"burl": redirect.burl})
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.zoidberg.auth_token.key}"
        )
        response = self.client.put(url, data, format="json")
        self.assertEquals(response.status_code, 403)

    def test_update_put_unauthorized(self):
        redirect = BriefURL.objects.create(user=self.kif, url=self.url, site=self.site)
        data = {
            "url": "https://facebook.com",
            "description": "friendface",
            "burl": "zuck",
        }
        url = reverse("burls:burls-detail", kwargs={"burl": redirect.burl})
        response = self.client.put(url, data, format="json")
        self.assertEquals(response.status_code, 401)

    def test_update_site2_burl_as_site1_editor(self):
        redirect = BriefURL.objects.create(
            user=self.farnsworth, url=self.url, site=self.site2, description="old man"
        )
        data = {"url": "https://facebook.com", "description": "friendface"}
        url = reverse("burls:burls-detail", kwargs={"burl": redirect.burl})
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.amy.auth_token.key}")
        response = self.client.patch(url, data, format="json")
        self.assertEquals(response.status_code, 404)


class BurlDeleteTests(BurlApiTestCase):
    def test_delete_by_admin_as_superuser(self):
        redirect = BriefURL.objects.create(
            user=self.leela, url=self.url, site=self.site
        )
        url = reverse("burls:burls-detail", kwargs={"burl": redirect.burl})
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.bender.auth_token.key}"
        )
        delete = self.client.delete(url)
        self.assertEquals(delete.status_code, 204)
        self.assertEquals(len(BriefURL.objects.filter(burl=redirect.burl)), 0)

    def test_delete_by_creator_as_creator(self):
        redirect = BriefURL.objects.create(user=self.kif, url=self.url, site=self.site2)
        url = reverse("burls:burls-detail", kwargs={"burl": redirect.burl})
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.kif.auth_token.key}")
        response = self.client.delete(url, SERVER_NAME=self.site2.domain)
        self.assertEquals(response.status_code, 204)
        self.assertEquals(len(BriefURL.objects.filter(burl=redirect.burl)), 0)

    def test_delete_by_editor_as_creator(self):
        redirect = BriefURL.objects.create(user=self.amy, url=self.url, site=self.site)
        url = reverse("burls:burls-detail", kwargs={"burl": redirect.burl})
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.fry.auth_token.key}")
        delete = self.client.delete(url)
        self.assertEquals(delete.status_code, 404)
        self.assertEquals(len(BriefURL.objects.filter(burl=redirect.burl)), 1)

    def test_delete_by_creator_as_admin(self):
        redirect = BriefURL.objects.create(user=self.fry, url=self.url, site=self.site)
        url = reverse("burls:burls-detail", kwargs={"burl": redirect.burl})
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.leela.auth_token.key}")
        response = self.client.delete(url)
        self.assertEquals(response.status_code, 204)
        self.assertEquals(len(BriefURL.objects.filter(burl=redirect.burl)), 0)

    def test_delete_by_creator_as_editor(self):
        redirect = BriefURL.objects.create(user=self.fry, url=self.url, site=self.site)
        url = reverse("burls:burls-detail", kwargs={"burl": redirect.burl})
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.amy.auth_token.key}")
        response = self.client.delete(url)
        self.assertEquals(response.status_code, 403)
        self.assertEquals(len(BriefURL.objects.filter(burl=redirect.burl)), 1)

    def test_delete_no_domain(self):
        redirect = BriefURL.objects.create(user=self.amy, url=self.url, site=self.site)
        url = reverse("burls:burls-detail", kwargs={"burl": redirect.burl})
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.farnsworth.auth_token.key}"
        )
        delete = self.client.delete(url)
        self.assertEquals(delete.status_code, 403)
        self.assertEquals(len(BriefURL.objects.filter(burl=redirect.burl)), 1)

    def test_delete_site1_burl_as_site2_admin(self):
        redirect = BriefURL.objects.create(user=self.fry, url=self.url, site=self.site)
        url = reverse("burls:burls-detail", kwargs={"burl": redirect.burl})
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.farnsworth.auth_token.key}"
        )
        delete = self.client.delete(url)
        self.assertEquals(delete.status_code, 403)
        self.assertEquals(len(BriefURL.objects.filter(burl=redirect.burl)), 1)

    def test_delete_unauthorized(self):
        redirect = BriefURL.objects.create(user=self.amy, url=self.url, site=self.site)
        url = reverse("burls:burls-detail", kwargs={"burl": redirect.burl})
        response = self.client.delete(url)
        self.assertEquals(response.status_code, 401)
        self.assertEquals(len(BriefURL.objects.filter(burl=redirect.burl)), 1)
