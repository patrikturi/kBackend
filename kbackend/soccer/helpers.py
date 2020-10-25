import logging

from rest_framework.exceptions import ValidationError

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

    logger.info({'event': 'create_stat', 'created': created, **create_data})

    return created


def create_stat(username, data):

    if not username:
        raise ValidationError('Username was not provided')

    user = User.get_or_create(username)
    data['user'] = user.id

    serializer = SoccerStatCreateSerializer(data=data)
    serializer.is_valid(raise_exception=True)

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

    logger.info({'event': 'create_match', **data})

    return match


def create_match_with_users(competition_name, home_team_name, away_team_name, home_players, away_players):
    match = Match.objects.create(competition_name=competition_name, home_team=home_team_name, away_team=away_team_name)

    home_participations = [MatchParticipation(user=user, match=match, side='home') for user in home_players]
    MatchParticipation.objects.bulk_create(home_participations)

    away_participartions = [MatchParticipation(user=user, match=match, side='away') for user in away_players]
    MatchParticipation.objects.bulk_create(away_participartions)

    User.bulk_add_match(home_players + away_players)

    return match
