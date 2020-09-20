from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from users.auth_helpers import get_basic_auth_username, basic_auth_denied
from soccer.helpers import perform_create_stat, perform_create_match


class SoccerStats(APIView):

    def post(self, request):
        auth_header = request.headers.get('Authorization')

        if not get_basic_auth_username(auth_header):
            return basic_auth_denied()

        return perform_create_stat(request.data)


class Matches(APIView):

    def post(self, request):
        auth_header = request.headers.get('Authorization')

        if not get_basic_auth_username(auth_header):
            return basic_auth_denied()

        match = perform_create_match(request.data)

        return Response({'id': match.id}, status=status.HTTP_201_CREATED)
