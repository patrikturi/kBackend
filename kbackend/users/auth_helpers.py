from base64 import b64decode

from django.conf import settings
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated
from rest_framework.response import Response


def get_basic_auth_username(auth_header):
    auth_header_split = auth_header.split(' ') if auth_header else []
    if len(auth_header_split) < 2:
        return None

    auth_type = auth_header_split[0]
    if auth_type.lower() != 'basic':
        return None

    auth_token = b64decode(auth_header_split[1]).decode('ascii')
    if ':' not in auth_token:
        return None

    if auth_token not in settings.BASIC_TOKENS:
        return None

    return auth_token.split(':')[0]


def basic_auth_denied():
    return Response(status=status.HTTP_401_UNAUTHORIZED, headers={'WWW-Authenticate': 'Basic realm="Users"'})


def auth_required(function):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise NotAuthenticated()
        return function(request, *args, **kwargs)
    return wrapper
