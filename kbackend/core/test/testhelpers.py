from unittest.mock import patch, DEFAULT

from django.test import TestCase as DjangoTestCase
from base64 import b64encode


class TestCase(DjangoTestCase):

    _valid_token = b64encode(b'debug:token').decode('ascii')
    _invalid_token = b64encode(b'debug:wrong-password').decode('ascii')
    valid_auth = f'basic {_valid_token}'
    invalid_auth = f'basic {_invalid_token}'

    dummy_uuid = '2e81fb58-f191-4c0e-aaa9-a41c92f689fa'

    def using(self, context_manager):
        enter_value = context_manager.__enter__()
        self.addCleanup(context_manager.__exit__)
        return enter_value

    def patch(self, target, new=DEFAULT, spec=None, create=False, mocksignature=False, spec_set=None, autospec=False, new_callable=None, **kwargs):
        return self.using(patch(target=target, new=new, spec=spec, create=create, mocksignature=mocksignature, spec_set=spec_set, autospec=autospec, new_callable=new_callable, **kwargs))
