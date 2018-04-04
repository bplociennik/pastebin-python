import os
from unittest import TestCase

from pastebiner import Pastebin, APIKeyError


class TestPastebin(TestCase):
    def setUp(self):
        self.api_dev_key = os.environ.get('PASTEBIN_API_DEV_KEY')
        self.api_login = os.environ.get('PASTEBIN_API_LOGIN', '')
        self.api_password = os.environ.get('PASTEBIN_API_PASSWORD', '')

    def test_create_object_without_dev_key(self):
        """Should raise Exception when dev_key is not given"""
        try:
            Pastebin()
            assert False
        except Exception:
            assert True

    def test_create_object_with_empty_dev_key(self):
        """Should raise APIKeyError when dev_key is empty"""
        try:
            Pastebin(dev_key='').trending()
        except APIKeyError as e:
            self.assertTrue(Pastebin.API_ERRORS['invalid_dev_key'], e)

    def test_create_object_with_none_dev_key(self):
        """Should raise APIKeyError when dev_key is None"""
        try:
            Pastebin(dev_key=None).trending()
        except APIKeyError as e:
            self.assertTrue(Pastebin.API_ERRORS['invalid_dev_key'], e)

    def test_create_object_with_correct_dev_key(self):
        """Should return data without any exception"""
        Pastebin(dev_key=self.api_dev_key).trending()

    def test_login_with_invalid_credentials(self):
        """Should raise APIKeyError when login is invalid"""
        try:
            Pastebin(dev_key=self.api_dev_key).login('fake', 'fake')
        except APIKeyError as e:
            self.assertTrue(Pastebin.API_ERRORS['invalid_login'], e)
