from unittest.mock import patch
from base64 import b64encode

from django.test import TestCase
from users.models import User


class SoccerStatsTestCase(TestCase):

    def test_invalid_token(self):
        User.objects.create(username='user')
        invalid_token = b64encode(b'debug:wrong-password').decode('ascii')

        valid_data = {'username': 'user', 'stat_uuid':'some-uuid', 'stat_type': 'goal', 'value': 1}
        response = self.client.post('/api/v1/soccer/stats/',
            valid_data, HTTP_AUTHORIZATION=f'basic {invalid_token}')

        self.assertEqual(401, response.status_code)

    def test_success(self):
        User.objects.create(username='user')
        valid_token = b64encode(b'debug:token').decode('ascii')

        valid_data = {'username': 'user', 'stat_uuid':'someuuid', 'stat_type': 'goal', 'value': 1}
        response = self.client.post('/api/v1/soccer/stats/',
            valid_data, HTTP_AUTHORIZATION=f'basic {valid_token}', content_type='application/json')

        self.assertEqual(201, response.status_code)
