from ratelimit.exceptions import Ratelimited
from rest_framework.views import exception_handler
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated
from rest_framework.response import Response
from rest_framework import status

from core.helpers import log_ratelimit


def custom_exception_handler(ex, context):

    if isinstance(ex, (AuthenticationFailed, NotAuthenticated)):
        return Response(ex.default_detail, status=status.HTTP_401_UNAUTHORIZED)
    elif isinstance(ex, Ratelimited):
        log_ratelimit(context['request'])
        return Response('Ratelimited', status=status.HTTP_429_TOO_MANY_REQUESTS)

    # Call REST framework's default exception handler
    return exception_handler(ex, context)
