from rest_framework.views import exception_handler
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(ex, context):

    if isinstance(ex, (AuthenticationFailed, NotAuthenticated)):
        return Response(ex.default_detail, status=status.HTTP_401_UNAUTHORIZED)

    # Call REST framework's default exception handler
    return exception_handler(ex, context)
