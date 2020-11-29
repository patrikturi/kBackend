from core.test.testhelpers import TestCase

from users.models import User
from soccer.models import Match, MatchParticipation


class MatchParticipationTestCase(TestCase):

    def test_create_team(self):
        user1 = User.objects.create(username='user1')
        user2 = User.objects.create(username='user2')
        match = Match.objects.create(home_team='home team', away_team='away team')

        MatchParticipation.objects.bulk_create_team(match, [user1, user2], side='home')

        participations = MatchParticipation.objects.filter(match=match).all()
        self.assertEqual(set(['user1', 'user2']), set(p.user.username for p in participations))
