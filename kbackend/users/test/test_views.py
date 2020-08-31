from unittest.mock import patch, Mock

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.test import Client, TestCase
from base64 import b64encode

from users.models import User


class PasswordResetTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.dummy_auth = 'basic some-token'

    @patch('users.views.get_basic_auth_username')
    def test_with_invalid_auth(self, get_basic_auth_username_mock):
        get_basic_auth_username_mock.return_value = None

        response = self.client.post('/api/v1/users/reset-password/')

        self.assertEqual(401, response.status_code)

    @patch('users.views.get_basic_auth_username')
    def test_without_username(self, get_basic_auth_username_mock):
        get_basic_auth_username_mock.return_value = 'script1'

        response = self.client.post('/api/v1/users/reset-password/', {}, HTTP_AUTHORIZATION=self.dummy_auth)

        self.assertEqual(400, response.status_code)

    @patch('users.views.get_basic_auth_username')
    def test_without_uuid(self, get_basic_auth_username_mock):
        get_basic_auth_username_mock.return_value = 'script1'

        response = self.client.post('/api/v1/users/reset-password/', {'username': 'john.smith'}, HTTP_AUTHORIZATION=self.dummy_auth)

        self.assertEqual(400, response.status_code)

    @patch('users.views.get_basic_auth_username')
    def test_with_invalid_username(self, get_basic_auth_username_mock):
        get_basic_auth_username_mock.return_value = 'script1'

        response = self.client.post('/api/v1/users/reset-password/', {'username': 'john smith', 'uuid': random_uuid()}, HTTP_AUTHORIZATION=self.dummy_auth)

        self.assertEqual(400, response.status_code)

    @patch('users.views.get_basic_auth_username')
    def test_with_nonexistent_user(self, get_basic_auth_username_mock):
        get_basic_auth_username_mock.return_value = 'script1'

        response = self.client.post('/api/v1/users/reset-password/',
            {'username': 'john.smith', 'uuid': random_uuid()}, HTTP_AUTHORIZATION=self.dummy_auth)

        self.assertEqual(200, response.status_code)
        self.assertTrue('pass' in response.data)

        user = authenticate(username='john.smith', password=response.data['pass'])
        self.assertIsNotNone(user)

    @patch('users.views.get_basic_auth_username')
    def test_with_existing_user(self, get_basic_auth_username_mock):
        User.objects.create_user('john.smith', password='existing-password')

        get_basic_auth_username_mock.return_value = 'script1'

        response = self.client.post('/api/v1/users/reset-password/',
            {'username': 'john.smith', 'uuid': random_uuid()}, HTTP_AUTHORIZATION=self.dummy_auth)

        self.assertEqual(200, response.status_code)
        self.assertTrue('pass' in response.data)
        self.assertNotEqual('existing-password', response.data['pass'])

        user = authenticate(username='john.smith', password=response.data['pass'])
        self.assertIsNotNone(user)


class LoginTestCase(TestCase):

    def test_success(self):
        username = 'bobby.marley'
        password = 'Thepassword123'
        User.objects.create_user(username, uuid=random_uuid(), password=password)

        response = self.client.post('/api/v1/users/login/', {'username': username, 'password': password})

        self.assertEqual(200, response.status_code)
        self.assertIsNotNone(response.cookies.get('sessionid'))

    def test_with_wrong_password(self):
        username = 'bobby.marley'
        password = 'Thepassword123'
        User.objects.create_user(username, uuid=random_uuid(), password=password)

        response = self.client.post('/api/v1/users/login/', {'username': username, 'password': 'The-wrong-password'})

        self.assertEqual(401, response.status_code)
        self.assertIsNone(response.cookies.get('sessionid'))


def random_uuid():
    return '2e81fb58-f191-4c0e-aaa9-a41c92f689fa'
