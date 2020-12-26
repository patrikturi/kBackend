import logging

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404
from ratelimit.core import is_ratelimited
from ratelimit.exceptions import Ratelimited
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
import nanoid

from users.models import User
from core.basic_auth import ServerBasicAuthentication
from users.serializers import UserListItem, UserProfileSerializer, UserProfileEditSerializer, LoginSerializer, PrivateUserProfileSerializer
from users.helpers import get_test_users, normalize_display_name, to_username, input_to_username

logger = logging.getLogger('users')


class PasswordResetView(APIView):

    authentication_classes = [ServerBasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return self.reset_password(request.data)

    @classmethod
    def reset_password(cls, data):
        new_password = nanoid.generate(size=20)
        display_name = normalize_display_name(data.get('username'))
        username = to_username(display_name)
        email = data.get('email', '')
        uuid = data.get('uuid')

        try:
            user, is_created = User.objects.reset_password(username, display_name, email, uuid, new_password)
        except ValidationError:
            logger.info({'event': 'password_reset_failed', 'username': username, 'uuid': uuid})
            raise

        logger.info(
            {
                'event': 'password_reset_success',
                'username': user.username,
                'uuid': user.uuid,
                'is_created': is_created
            }
        )

        return Response({'password': new_password})


class LoginView(APIView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ratelimit_config = {'key': 'ip', 'rate': '10/30m', 'fn': self.post}

    def post(self, request):
        return self.login(request, request.user, request.POST)

    def login(self, request, user, data):

        if user.is_authenticated:
            return self._ok_response(user, request.META['CSRF_COOKIE'])
        if is_ratelimited(request, **self.ratelimit_config, increment=False):
            raise Ratelimited()

        username = input_to_username(data.get('username'))
        password = data.get('password')
        user = authenticate(request, username=username, password=password)

        if not user:
            is_ratelimited(request, **self.ratelimit_config, increment=True)
            logger.info({'event': 'login_failed', 'username': username})
            raise AuthenticationFailed()

        login(request, user)
        logger.info({'event': 'login_success', 'username': user.username})

        return self._ok_response(user, request.META['CSRF_COOKIE'])

    def _ok_response(self, user, csrftoken):
        response = Response(LoginSerializer(user).data)
        response.data['csrftoken'] = csrftoken
        return response


class LogoutView(APIView):

    def get(self, request):
        if request.user.is_authenticated:
            logger.info({'event': 'logout', 'username': request.user.username})
        logout(request)
        return Response({})


class UserSearchview(APIView):

    def get(self, request):
        return self.search(request.GET)

    @classmethod
    def search(cls, parameters):
        username = input_to_username(parameters.get('username', ''))
        if len(username) < 3:
            raise ValidationError(f'Search term "{username}" is too short')

        found_users = User.objects.search_by_name(username)

        data = UserListItem(found_users, many=True).data
        return Response(data)


class PlayerMarketplaceView(APIView):

    def get(self, request):
        found_users = User.objects.search_marketplace()

        data = UserListItem(found_users, many=True).data
        return Response(data)


class UserProfileView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)

        return Response(UserProfileSerializer(user).data)

    def patch(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        if request.user.id != user_id and not request.user.is_superuser:
            raise PermissionDenied()

        serializer = UserProfileEditSerializer(user, request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        logger.info({'event': 'update_user_profile', 'username': user.username, 'data': request.data})
        return Response(serializer.data)


class PrivateUserProfileView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = get_object_or_404(User, id=request.user.id)

        return Response(PrivateUserProfileSerializer(user).data)


class TestUsersView(APIView):

    authentication_classes = [ServerBasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        test_users = get_test_users()

        data = [{'username': user.username} for user in test_users]
        return Response(data)

    def post(self, request):
        username = f'test-{nanoid.generate(size=4)}'

        new_user = User.objects.create_user(username, display_name=username, is_test=True)

        return Response({'username': new_user.username})


class ChangePasswordView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        old_password = request.POST.get('old_password', '')
        new_password = request.POST.get('new_password', '')
        request.user.change_password(old_password, new_password)

        logger.info({'event': 'change_password', 'username': request.user.username})
        return Response({})
