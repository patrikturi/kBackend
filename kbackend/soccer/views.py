import rest_framework.response
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from users.auth_helpers import get_basic_auth_username, basic_auth_denied
from soccer.helpers import perform_create_stat, create_match_with_users
from users.models import User


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

        # TODO: assert user not in both teams
        data = request.data
        home_players = User.bulk_get_or_create(data['home_players'])
        away_players = User.bulk_get_or_create(data['away_players'])

        match = create_match_with_users(data.get('competition', ''),
                                        data['home_team'],
                                        data['away_team'],
                                        home_players,
                                        away_players)

        return Response({'id': match.id}, status=status.HTTP_201_CREATED)
