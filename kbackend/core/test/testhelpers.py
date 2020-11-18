from django.test import TestCase
from base64 import b64encode


class BasicAuthTestCase(TestCase):

    def setUp(self):
        super().setUp()
        valid_token = b64encode(b'debug:token').decode('ascii')
        invalid_token = b64encode(b'debug:wrong-password').decode('ascii')
        self.valid_auth = f'basic {valid_token}'
        self.invalid_auth = f'basic {invalid_token}'
