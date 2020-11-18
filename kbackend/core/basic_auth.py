from django.contrib.auth.models import AnonymousUser
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed

from base64 import b64decode

from django.conf import settings


class ServerBasicAuthentication(authentication.BaseAuthentication):
    """ Authenticate a request by another server """

    def authenticate(self, request):

        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None

        basic_token = decode_basic_token(auth_header)
        if basic_token not in settings.BASIC_TOKENS:
            raise AuthenticationFailed('Invalid username or password')

        username = basic_token.split(':')[0]
        return (BasicUser(username), None)


class BasicUser(AnonymousUser):

    def __init__(self, basic_username):
        self.basic_username = basic_username

    @property
    def is_authenticated(self):
        return True


def decode_basic_token(auth_header):
    auth_header_split = auth_header.split(' ') if auth_header else []
    if len(auth_header_split) < 2:
        return None

    auth_type = auth_header_split[0]
    if auth_type.lower() != 'basic':
        return None

    return b64decode(auth_header_split[1]).decode('ascii')
