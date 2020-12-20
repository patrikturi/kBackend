from django.test import override_settings

from core import decorators
from core.test.testhelpers import TestCase
from users.models import User


class AdminTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_superuser(username='admin', password='1234')

    def test_success(self):
        response = self.client.post('/adminsite/login/', {'username': 'admin', 'password': '1234'})
        self.assertEqual(302, response.status_code)

    def test_ratelimited(self):
        decorators.ratelimit_config['rate'] = '1/30m'

        with override_settings(RATELIMIT_ENABLE=True):
            for i in range(2):
                response = self.client.post('/adminsite/login/', {'username': 'admin', 'password': 'wrong-password'})
                self.assertEqual(200, response.status_code)

            response = self.client.post('/adminsite/login/', {'username': 'admin', 'password': '1234'})
            self.assertEqual(429, response.status_code)
