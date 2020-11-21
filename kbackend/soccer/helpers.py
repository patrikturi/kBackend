import logging

from soccer.serializers import SoccerStatCreateSerializer
from soccer.models import MatchParticipation, Match
from users.models import User
from soccer.serializers import MatchCreateSerializer

logger = logging.getLogger('soccer')


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
