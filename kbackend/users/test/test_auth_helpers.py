from base64 import b64encode

from django.test import TestCase

from users.auth_helpers import get_basic_auth_username


class GetBasicAuthUsernameTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.valid_token = b64encode(b'debug:token').decode('ascii')

    def test_with_valid_token(self):
        username = get_basic_auth_username(f'basic {self.valid_token}')

        self.assertEqual('debug', username)

    def test_without_auth_header(self):
        username = get_basic_auth_username(None)

        self.assertIsNone(username)

    def test_with_invalid_auth_header(self):
        username = get_basic_auth_username('invalid-header')

        self.assertIsNone(username)

    def test_with_invalid_auth_type(self):
        username = get_basic_auth_username(f'invalid-auth-type {self.valid_token}')

        self.assertIsNone(username)

    def test_with_invalid_token(self):
        invalid_token = b64encode(b'invalid-token').decode('ascii')

        username = get_basic_auth_username(f'basic {invalid_token}')

        self.assertIsNone(username)

    def test_with_wrong_password(self):
        token = b64encode(b'debug:wrong-password').decode('ascii')

        username = get_basic_auth_username(f'basic {token}')

        self.assertIsNone(username)
