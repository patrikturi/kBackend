import logging

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
import nanoid

from users.auth_helpers import get_basic_auth_username, basic_auth_denied
from users.models import User
from users.serializers import UserListItem, UserProfileSerializer, UserProfileEditSerializer
from users.helpers import get_test_users

logger = logging.getLogger('users')


class PasswordReset(APIView):

    def post(self, request):
        auth_header = request.headers.get('Authorization')

        if not get_basic_auth_username(auth_header):
            return basic_auth_denied()

        new_password = nanoid.generate(size=20)
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
        if request.user.is_authenticated:
            return Response()
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
        if request.user.is_authenticated:
            logger.info({'event': 'logout', 'username': user.username})
        logout(request)
        return Response()


class UserSearch(APIView):

    def get(self, request):
        username = request.GET.get('username', '').lower()
        if len(username) < 3:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        found_users = User.objects.filter(username__contains=username).all().order_by('username')[:100]

        user_username = request.user.username if request.user else ''
        logger.info({'event': 'user_search',
                     'username': user_username,
                     'username_param': username,
                     'result_count': len(found_users)})

        data = [UserListItem(user).data for user in found_users]
        return Response(data)


class PlayerMarketplace(APIView):

    def get(self, request):
        found_users = User.objects.filter(available_for_transfer=True).all().order_by('username')[:100]

        data = [UserListItem(user).data for user in found_users]
        return Response(data)


class UserProfile(APIView):

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)

        return Response(UserProfileSerializer(user).data)

    @method_decorator(login_required)
    def patch(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        if request.user.id != user_id and not request.user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = UserProfileEditSerializer(user, request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response()

        return Response(status=status.HTTP_400_BAD_REQUEST)


class TestUsers(APIView):

    def get(self, request):
        auth_header = request.headers.get('Authorization')

        if not get_basic_auth_username(auth_header):
            return basic_auth_denied()

        test_users = get_test_users()

        data = [{'username': user.username} for user in test_users]
        return Response(data)

    def post(self, request):
        auth_header = request.headers.get('Authorization')

        if not get_basic_auth_username(auth_header):
            return basic_auth_denied()

        username = f'test-{nanoid.generate(size=4)}'

        new_user = User.objects.create_user(username, is_test=True)

        return Response(data={'username': username})
