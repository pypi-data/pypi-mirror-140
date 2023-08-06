from django.test import TestCase

from django_burl import utils


class MakeBurlTest(TestCase):
    def test_make_burl_return_string(self):
        burl = utils.make_burl()
        self.assertIsInstance(burl, str)
