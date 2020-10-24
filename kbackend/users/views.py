import logging

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied, ValidationError
import nanoid

from users.auth_helpers import get_basic_auth_username, basic_auth_denied
from users.models import User
from users.serializers import UserListItem, UserProfileSerializer, UserProfileEditSerializer
from users.helpers import get_test_users, normalize_display_name, to_username, input_to_username

logger = logging.getLogger('users')


class PasswordResetView(APIView):

    def post(self, request):
        auth_header = request.headers.get('Authorization')

        if not get_basic_auth_username(auth_header):
            return basic_auth_denied()

        new_password = nanoid.generate(size=20)
        display_name = normalize_display_name(request.data.get('username'))
        username = to_username(display_name)
        email = request.data.get('email', '')
        uuid = request.data.get('uuid')
        try:
            user, is_created = User.reset_password(username, display_name, email, uuid, new_password)
        except ValidationError:
            logger.info({'event': 'password_reset_failed', 'username': username, 'uuid': uuid})
            raise

        logger.info({'event': 'password_reset_success',
                     'username': user.username,
                     'uuid': user.uuid,
                     'is_created': is_created})

        return Response({'password': new_password})


class LoginView(APIView):

    @method_decorator(ensure_csrf_cookie)
    def post(self, request):
        if request.user.is_authenticated:
            return Response({'id': request.user.id, 'username': request.user.username})
        username = input_to_username(request.POST.get('username'))
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if not user:
            logger.info({'event': 'login_failed', 'username': username})
            raise AuthenticationFailed()

        login(request, user)

        logger.info({'event': 'login_success', 'username': user.username})

        return Response({'id': user.id, 'username': username})


class LogoutView(APIView):

    def get(self, request):
        if request.user.is_authenticated:
            logger.info({'event': 'logout', 'username': request.user.username})
        logout(request)
        return Response({})


class UserSearchview(APIView):

    def get(self, request):
        username = input_to_username(request.GET.get('username', ''))
        if len(username) < 3:
            raise ValidationError(f'Search term "{username}" is too short')

        found_users = User.objects.filter(username__contains=username).all().order_by('username')[:100]

        user_username = request.user.username if request.user else ''
        logger.info({'event': 'user_search',
                     'username': user_username,
                     'username_param': username,
                     'result_count': len(found_users)})

        data = [UserListItem(user).data for user in found_users]
        return Response(data)


class PlayerMarketplaceView(APIView):

    def get(self, request):
        found_users = User.objects.filter(available_for_transfer=True).all().order_by('username')[:100]

        data = [UserListItem(user).data for user in found_users]
        return Response(data)


class UserProfileView(APIView):

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)

        return Response(UserProfileSerializer(user).data)

    @method_decorator(ensure_csrf_cookie)
    @method_decorator(login_required)
    def patch(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        if request.user.id != user_id and not request.user.is_superuser:
            raise PermissionDenied()

        serializer = UserProfileEditSerializer(user, request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class TestUsersView(APIView):

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

        new_user = User.objects.create_user(username, display_name=username, is_test=True)

        return Response({'username': new_user.username})
