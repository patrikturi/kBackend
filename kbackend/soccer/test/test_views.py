import json

from users.models import User
from users.test.testhelpers import ViewTestCase


class SoccerStatsTestCase(ViewTestCase):

    def test_invalid_token(self):
        User.objects.create(username='user')

        valid_data = {'username': 'user', 'stat_uuid': 'some-uuid', 'stat_type': 'goal', 'value': 1}
        response = self.client.post('/api/v1/soccer/stats/', valid_data,
                                    HTTP_AUTHORIZATION=self.invalid_auth)

        self.assertEqual(401, response.status_code)

    def test_success(self):
        User.objects.create(username='user')

        valid_data = {'username': 'user', 'stat_uuid': 'someuuid', 'stat_type': 'goal', 'value': 1}
        response = self.client.post('/api/v1/soccer/stats/', valid_data,
                                    HTTP_AUTHORIZATION=self.valid_auth, content_type='application/json')

        self.assertEqual(201, response.status_code)


class CreateMatchTestCase(ViewTestCase):

    def test_invalid_auth(self):
        valid_data = {'home_team': 'Team A', 'away_team': 'Team B', 'home_players': ['userA', 'userB'], 'away_players': ['userC', 'userD']}
        response = self.client.post('/api/v1/soccer/matches/', valid_data,
                                    HTTP_AUTHORIZATION=self.invalid_auth, content_type='application/json')

        self.assertEqual(401, response.status_code)

    def test_success(self):
        valid_data = {'home_team': 'Team A', 'away_team': 'Team B', 'home_players': ['userA', 'userB'], 'away_players': ['userC', 'userD']}
        response = self.client.post('/api/v1/soccer/matches/', valid_data,
                                    HTTP_AUTHORIZATION=self.valid_auth, content_type='application/json')

        self.assertEqual(201, response.status_code)
        response_data = json.loads(response.content)
        self.assertTrue(isinstance(response_data['id'], int))
