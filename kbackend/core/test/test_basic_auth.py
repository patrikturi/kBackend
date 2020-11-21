from base64 import b64encode

from core.basic_auth import decode_basic_token
from core.test.testhelpers import TestCase


class BasicAuthTest(TestCase):

    def setUp(self):
        super().setUp()

    def test_with_invalid_password(self):
        response = self.client.get('/test/basic-auth/', HTTP_AUTHORIZATION=self.invalid_auth)

        self.assertEqual(401, response.status_code)

    def test_with_valid_password(self):
        response = self.client.get('/test/basic-auth/', HTTP_AUTHORIZATION=self.valid_auth)

        self.assertEqual(200, response.status_code)


class DecodeBasicTokenTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.valid_auth = b64encode(b'user:password').decode('ascii')

    def test_with_valid_token(self):
        basic_token = decode_basic_token(f'basic {self.valid_auth}')

        self.assertEqual('user:password', basic_token)

    def test_with_none(self):
        basic_token = decode_basic_token(None)

        self.assertIsNone(basic_token)

    def test_with_invalid_auth_scheme(self):
        basic_token = decode_basic_token(f'invalid-scheme {self.valid_auth}')

        self.assertIsNone(basic_token)

    def test_with_invalid_auth(self):
        basic_token = decode_basic_token('invalid-auth')

        self.assertIsNone(basic_token)
