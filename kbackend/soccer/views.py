import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from core.basic_auth import ServerBasicAuthentication
from users.models import User
from soccer.models import MatchParticipation, Match
from soccer.serializers import MatchSerializer, MatchCreateSerializer, SoccerStatCreateSerializer

logger = logging.getLogger('soccer')


class SoccerStatsView(APIView):

    authentication_classes = [ServerBasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return self.create_stat(request.data)

    @classmethod
    def create_stat(cls, data):
        create_data = dict(data)
        username = create_data.pop('username', None)

        user = User.get_or_create(username)
        create_data['user'] = user.id

        serializer = SoccerStatCreateSerializer(data=create_data)
        stat, created = serializer.get_or_create()

        if created:
            user.add_stat(data['stat_type'], data['value'])

        logger.info({'event': 'create_stat', 'created': created, 'data': create_data})

        ret_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(serializer.data, status=ret_status)


class MatchesView(APIView):

    authentication_classes = [ServerBasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return self.create_match(request.data)

    @classmethod
    def create_match(cls, data):
        serializer = MatchCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        match = Match.objects.create(
            competition_name=data.get('competition', ''),
            home_team=data['home_team'],
            away_team=data['away_team'])

        home_players = User.bulk_get_or_create(data['home_players'])
        away_players = User.bulk_get_or_create(data['away_players'])

        MatchParticipation.objects.bulk_create_team(match, home_players, side='home')
        MatchParticipation.objects.bulk_create_team(match, away_players, side='away')

        User.bulk_add_match(home_players + away_players)

        logger.info({'event': 'create_match', 'data': serializer.data})

        match_serializer = MatchSerializer(match)
        return Response(match_serializer.data, status=status.HTTP_201_CREATED)
