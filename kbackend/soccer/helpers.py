import logging

from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers

from soccer.serializers import SoccerStatCreateSerializer
from soccer.models import SoccerStat, MatchParticipation, Match
from users.models import User
from soccer.serializers import MatchCreateSerializer

logger = logging.getLogger('soccer')


def perform_create_stat(data):
    username = data.get('username')

    create_data = dict(data)
    create_data.pop('username', None)
    stat, created = create_stat(username, create_data)

    if not stat:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    ret_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK

    logger.info({'event': 'create_stat', 'created': created, **create_data})

    return Response({}, status=ret_status)


def create_stat(username, data):

    if not username:
        return None, False

    user = User.get_or_create(username)
    data['user'] = user.id

    serializer = SoccerStatCreateSerializer(data=data)
    if not serializer.is_valid():
        return None, False

    stat_uuid = data['stat_uuid']
    stat_type = data['stat_type']
    value = data['value']

    stat = SoccerStat.objects.filter(stat_uuid=stat_uuid).first()
    if stat:
        # Already exists
        return stat, False

    stat = serializer.save()
    user.add_stat(stat_type, value)
    return stat, True


def perform_create_match(data):
    serializer = MatchCreateSerializer(data=data)
    serializer.is_valid(raise_exception=True)

    home_players = User.bulk_get_or_create(data['home_players'])
    away_players = User.bulk_get_or_create(data['away_players'])

    match = create_match_with_users(data.get('competition', ''),
                                    data['home_team'],
                                    data['away_team'],
                                    home_players,
                                    away_players)
    return match


def create_match_with_users(competition_name, home_team_name, away_team_name, home_players, away_players):
    match = Match.objects.create(competition_name=competition_name, home_team=home_team_name, away_team=away_team_name)

    home_participations = [MatchParticipation(user=user, match=match, side='home') for user in home_players]
    MatchParticipation.objects.bulk_create(home_participations)

    away_participartions = [MatchParticipation(user=user, match=match, side='away') for user in away_players]
    MatchParticipation.objects.bulk_create(away_participartions)

    return match
