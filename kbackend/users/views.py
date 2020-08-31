import logging

from django.contrib.auth import authenticate, login, logout
from nanoid import generate
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from users.auth_helpers import get_basic_auth_username, basic_auth_denied
from users.models import User

logger = logging.getLogger('users')


class PasswordReset(APIView):

    def post(self, request):
        auth_header = request.headers.get('Authorization')

        if not get_basic_auth_username(auth_header):
            return basic_auth_denied()

        new_password = generate(size=20)
        username = request.data.get('username')
        uuid = request.data.get('uuid')
        user, is_created = User.reset_password(username, uuid, new_password)
        if not user:
            logger.info({'event': 'password_reset_failed', 'username': username, 'uuid': uuid})
            return Response(status=status.HTTP_400_BAD_REQUEST)

        logger.info({'event': 'password_reset_success',
                     'username': username,
                     'uuid': uuid,
                     'is_created': is_created})

        return Response({'pass': new_password})


class Login(APIView):

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if not user:
            logger.info({'event': 'login_failed', 'username': username})
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        login(request, user)

        logger.info({'event': 'login_success', 'username': user.username})

        return Response()


class Logout(APIView):

    def get(self, request):
        if request.user:
            logger.info({'event': 'logout', 'username': user.username})
        logout(request)
        return Response()
