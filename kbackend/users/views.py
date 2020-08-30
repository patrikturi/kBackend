from nanoid import generate
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from users.auth_helpers import get_basic_auth_username, basic_auth_denied
from users.models import User


class PasswordReset(APIView):

    def post(self, request):
        auth_header = request.headers.get('Authorization')

        if not get_basic_auth_username(auth_header):
            return basic_auth_denied()

        new_password = generate(size=20)
        data = request.data
        user = User.reset_password(data.get('username'), data.get('uuid'), new_password)
        if not user:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response({'pass': new_password})
