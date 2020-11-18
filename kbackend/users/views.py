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

from users.models import User, UserDetails
from core.basic_auth import ServerBasicAuthentication
from users.serializers import UserListItem, UserProfileSerializer, UserProfileEditSerializer, LoginSerializer, PrivateUserProfileSerializer, UserDetailsEditSerializer
from users.helpers import get_test_users, normalize_display_name, to_username, input_to_username

logger = logging.getLogger('users')


class PasswordResetView(APIView):

    authentication_classes = [ServerBasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
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

    def post(self, request):
        ratelimit_config = {'key': 'ip', 'rate': '10/30m', 'fn': self.post}

        if request.user.is_authenticated:
            return self._ok_response(request.user, request.META['CSRF_COOKIE'])
        if is_ratelimited(request, **ratelimit_config, increment=False):
            raise Ratelimited()

        username = input_to_username(request.POST.get('username'))
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if not user:
            is_ratelimited(request, **ratelimit_config, increment=True)
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
        username = input_to_username(request.GET.get('username', ''))
        if len(username) < 3:
            raise ValidationError(f'Search term "{username}" is too short')

        found_users = User.objects.filter(username__contains=username).all().order_by('username')[:100]

        data = [UserListItem(user).data for user in found_users]
        return Response(data)


class PlayerMarketplaceView(APIView):

    def get(self, request):
        found_users = User.objects.filter(available_for_transfer=True).all().order_by('username')[:100]

        data = [UserListItem(user).data for user in found_users]
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

        patch_data = {key: value for key, value in request.data.items() if key != 'user_details'}
        saved_user_details = None
        if 'user_details' in request.data:
            saved_user_details = self.update_user_details(user, request.data['user_details'])

        serializer = UserProfileEditSerializer(user, patch_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        saved_data = dict(serializer.data)
        if saved_user_details:
            saved_data['user_details'] = [saved_user_details]

        logger.info({'event': 'update_user_profile', 'username': user.username, 'data': saved_data})
        return Response(saved_data)

    @classmethod
    def update_user_details(cls, user, data):
        instance = UserDetails.objects.filter(user=user).first()
        if instance is None:
            data['user'] = user.id
            is_partial = False
        else:
            is_partial = True
        serializer = UserDetailsEditSerializer(instance, data, partial=is_partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data


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
