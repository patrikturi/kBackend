import json

from rest_framework.exceptions import ValidationError

from core.test.testhelpers import TestCase
from soccer.views import MatchesView, SoccerStatsView
from soccer.models import Match, SoccerStat, MatchParticipation
from users.models import User


class CreateStatTest(TestCase):

    def setUp(self):
        super().setUp()
        self.user = User.objects.create(username='user')
        self.view = SoccerStatsView

    def test_with_match(self):
        match = Match.objects.create()

        valid_data = {'username': 'user', 'stat_uuid': 'someuuid', 'stat_type': 'goal', 'value': 1, 'match': match.id}
        response = self.client.post('/api/v1/soccer/stats/', valid_data,
                                    HTTP_AUTHORIZATION=self.valid_auth, content_type='application/json')

        self.assertEqual(201, response.status_code)

        stat = SoccerStat.objects.get(user=self.user)
        self.assertTrue('id' in response.data)
        self.assertAllEqual('someuuid', stat.stat_uuid, response.data['stat_uuid'])
        self.assertAllEqual('goal', stat.stat_type, response.data['stat_type'])
        self.assertAllEqual(1, stat.value, response.data['value'])
        self.assertAllEqual(match.id, stat.match.id, response.data['match'])

        self.user.refresh_from_db()
        self.assertEqual(1, self.user.goals)

    def test_stat_already_exists(self):
        SoccerStat.objects.create(user=self.user, stat_uuid='someuuid', stat_type='goal', value=1)

        valid_data = {'username': 'user', 'stat_uuid': 'someuuid', 'stat_type': 'goal', 'value': 1}
        response = self.view.create_stat(valid_data)

        self.assertEqual(200, response.status_code)

        stat = SoccerStat.objects.get(user=self.user)
        self.assertTrue('id' in response.data)
        self.assertAllEqual('goal', stat.stat_type, response.data['stat_type'])

        self.user.refresh_from_db()
        self.assertEqual(0, self.user.goals)

    def test_username_not_provided(self):
        invalid_data = {'stat_uuid': 'someuuid', 'stat_type': 'goal', 'value': 1}
        self.assertRaises(ValidationError, lambda: self.view.create_stat(invalid_data))


class CreateMatchTest(TestCase):

    def test_with_competition(self):
        valid_data = {
            'home_team': 'Team A',
            'away_team': 'Team B',
            'home_players': ['userA', 'userB'],
            'away_players': ['userC', 'userD'],
            'competition': 'dummy-competition'
        }
        response = self.client.post('/api/v1/soccer/matches/', valid_data,
                                    HTTP_AUTHORIZATION=self.valid_auth, content_type='application/json')

        self.assertEqual(201, response.status_code)

        response_data = json.loads(response.content)
        self.assertTrue('id' in response_data)

        match = Match.objects.filter(competition_name='dummy-competition').first()

        self.assertEqual('dummy-competition', response_data['competition'])
        self.assertAllEqual('Team A', match.home_team, response_data['home_team'])
        self.assertAllEqual('Team B', match.away_team, response_data['away_team'])

        home_participation = MatchParticipation.objects.filter(match=match, side='home')
        self.assertEqual(2, len(home_participation))
        away_participation = MatchParticipation.objects.filter(match=match, side='away')
        self.assertEqual(2, len(away_participation))

        created_users = User.objects.filter(username__in=['usera', 'userb', 'userc', 'userd'])
        self.assertEqual(4, len(created_users))

    def test_without_competition(self):
        valid_data = {
            'home_team': 'Team 1',
            'away_team': 'Team 2',
            'home_players': ['userA', 'userB'],
            'away_players': ['userC', 'userD'],
        }
        response = MatchesView.create_match(valid_data)

        self.assertEqual(201, response.status_code)

        match = Match.objects.filter(home_team='Team 1', away_team='Team 2').first()
        self.assertIsNotNone(match)
