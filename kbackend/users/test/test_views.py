import json
import logging
from unittest.mock import patch

from django.contrib.auth import authenticate
from django.test import TestCase

from users.models import User, UserDetails
from users.test.testhelpers import ViewTestCase

logging.disable(logging.CRITICAL)


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

        response = self.client.post('/api/v1/users/reset-password/', {'username': 'JohN SmiTh'}, HTTP_AUTHORIZATION=self.dummy_auth)

        self.assertEqual(400, response.status_code)

    @patch('users.views.get_basic_auth_username')
    def test_with_invalid_username(self, get_basic_auth_username_mock):
        get_basic_auth_username_mock.return_value = 'script1'

        response = self.client.post('/api/v1/users/reset-password/', {'username': 'JohN SmiTh The Great', 'uuid': random_uuid()}, HTTP_AUTHORIZATION=self.dummy_auth)

        self.assertEqual(400, response.status_code)

    @patch('users.views.get_basic_auth_username')
    def test_with_nonexistent_user(self, get_basic_auth_username_mock):
        get_basic_auth_username_mock.return_value = 'script1'

        response = self.client.post('/api/v1/users/reset-password/',
                                    {'username': 'JohN SmiTh', 'email': 'john@gmail.com', 'uuid': random_uuid()}, HTTP_AUTHORIZATION=self.dummy_auth)

        self.assertEqual(200, response.status_code)
        self.assertTrue('password' in response.data)

        user = authenticate(username='john.smith', password=response.data['password'])
        self.assertIsNotNone(user)
        self.assertEqual('john@gmail.com', user.email)
        self.assertEqual('JohN SmiTh', user.display_name)

    @patch('users.views.get_basic_auth_username')
    def test_with_nonexistent_resident_user(self, get_basic_auth_username_mock):
        get_basic_auth_username_mock.return_value = 'script1'

        response = self.client.post('/api/v1/users/reset-password/',
                                    {'username': 'John Resident', 'email': 'john@gmail.com', 'uuid': random_uuid()}, HTTP_AUTHORIZATION=self.dummy_auth)

        self.assertEqual(200, response.status_code)
        self.assertTrue('password' in response.data)

        user = authenticate(username='john', password=response.data['password'])
        self.assertIsNotNone(user)
        self.assertEqual('john@gmail.com', user.email)
        self.assertEqual('John', user.display_name)

    @patch('users.views.get_basic_auth_username')
    def test_with_existing_user(self, get_basic_auth_username_mock):
        User.objects.create_user('john.smith', password='existing-password')

        get_basic_auth_username_mock.return_value = 'script1'

        response = self.client.post('/api/v1/users/reset-password/',
                                    {'username': 'JohN SmiTh', 'uuid': random_uuid()}, HTTP_AUTHORIZATION=self.dummy_auth)

        self.assertEqual(200, response.status_code)
        self.assertTrue('password' in response.data)
        self.assertNotEqual('existing-password', response.data['password'])

        user = authenticate(username='john.smith', password=response.data['password'])
        self.assertIsNotNone(user)


class LoginTestCase(TestCase):

    def test_success(self):
        username = 'bobby.marley'
        password = 'Thepassword123'
        User.objects.create_user(username, uuid=random_uuid(), password=password)

        response = self.client.post('/api/v1/users/login/', {'username': 'Bobby Marley', 'password': password})

        self.assertEqual(200, response.status_code)
        self.assertIsNotNone(response.cookies.get('sessionid'))
        response_data = json.loads(response.content)
        self.assertEqual(1, response_data['id'])
        self.assertEqual('bobby.marley', response_data['username'])

    def test_with_wrong_password(self):
        username = 'bobby.marley'
        password = 'Thepassword123'
        User.objects.create_user(username, uuid=random_uuid(), password=password)

        response = self.client.post('/api/v1/users/login/', {'username': 'Bobby Marley', 'password': 'The-wrong-password'})

        self.assertEqual(401, response.status_code)
        self.assertIsNone(response.cookies.get('sessionid'))


class UserSearchTestCase(TestCase):

    def test_success(self):
        User.objects.create_user('bobby.marley', uuid=random_uuid(), password='abcd')
        User.objects.create_user('john.smith', uuid=random_uuid(), password='abcdef')
        User.objects.create_user('big.bobman', uuid=random_uuid(), password='abcdef')

        response = self.client.get('/api/v1/users/search/?username=bob')

        self.assertEqual(200, response.status_code)

        usernames = [user['username'] for user in response.data]
        self.assertEqual(set(['bobby.marley', 'big.bobman']), set(usernames))

    def test_with_full_name(self):
        User.objects.create_user('bobby.marley', uuid=random_uuid(), password='abcd')
        User.objects.create_user('john.smith', uuid=random_uuid(), password='abcdef')
        User.objects.create_user('big.bobman', uuid=random_uuid(), password='abcdef')

        response = self.client.get('/api/v1/users/search/?username=Bobby%20M')

        self.assertEqual(200, response.status_code)

        usernames = [user['username'] for user in response.data]
        self.assertEqual(['bobby.marley'], usernames)

    def test_with_no_results(self):
        User.objects.create_user('john.smith', uuid=random_uuid(), password='abcd')

        response = self.client.get('/api/v1/users/search/?username=bob')

        self.assertEqual(200, response.status_code)
        self.assertEqual([], response.data)

    def test_with_too_short_username(self):
        response = self.client.get('/api/v1/users/search/?username=b')

        self.assertEqual(400, response.status_code)


class PlayerMarketplaceTestCase(TestCase):

    def test_success(self):
        User.objects.create_user('bobby.marley', available_for_transfer=False, uuid=random_uuid(), password='abcd')
        User.objects.create_user('john.smith', available_for_transfer=True, uuid=random_uuid(), password='abcdef')
        User.objects.create_user('big.bobman', available_for_transfer=False, uuid=random_uuid(), password='abcdef')
        User.objects.create_user('newplayer', available_for_transfer=True, uuid=random_uuid(), password='abcdef')

        response = self.client.get('/api/v1/users/marketplace/')

        self.assertEqual(200, response.status_code)

        usernames = [user['username'] for user in response.data]
        self.assertEqual(set(['john.smith', 'newplayer']), set(usernames))


class GetUserProfileTestCase(TestCase):

    def test_success(self):
        User.objects.create_user('bobby.marley', uuid=random_uuid(), password='abcd')
        user = User.objects.create_user('john.smith', uuid=random_uuid(), password='abcdef')
        User.objects.create_user('big.bobman', uuid=random_uuid(), password='abcdef')

        UserDetails.objects.create(user=user, biography='This is my bio.')

        response = self.client.get('/api/v1/users/profile/2/')

        self.assertEqual(200, response.status_code)
        self.assertEqual('john.smith', response.data['username'])
        self.assertEqual('This is my bio.', response.data['user_details'][0]['biography'])

    def test_not_found(self):
        response = self.client.get('/api/v1/users/profile/111/')

        self.assertEqual(404, response.status_code)


class PatchUserProfileTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.user1 = User.objects.create_user('bobby.marley', uuid=random_uuid(), password='abcd')
        self.user2 = User.objects.create_user('john.smith', uuid=random_uuid(), password='abcdef')

    def test_success(self):
        self.client.force_login(self.user1)

        response = self.client.patch('/api/v1/users/profile/1/', {'introduction': "Hi, I'm Bob!"}, content_type='application/json')

        self.assertEqual(200, response.status_code)
        self.user1.refresh_from_db()
        self.assertEqual("Hi, I'm Bob!", self.user1.introduction)
        response_data = json.loads(response.content)
        self.assertEqual("Hi, I'm Bob!", response_data['introduction'])

    def test_with_different_user(self):
        self.client.force_login(self.user2)

        response = self.client.patch('/api/v1/users/profile/1/', {'introduction': "Hi, I'm Bob!"}, content_type='application/json')

        self.assertEqual(403, response.status_code)


class CreateTestUserTestCase(ViewTestCase):

    def test_invalid_auth(self):
        response = self.client.post('/api/v1/users/test-users/', HTTP_AUTHORIZATION=self.invalid_auth)

        self.assertEqual(401, response.status_code)

    def test_success(self):
        response = self.client.post('/api/v1/users/test-users/', HTTP_AUTHORIZATION=self.valid_auth)

        self.assertEqual(200, response.status_code)
        response_data = json.loads(response.content)
        self.assertTrue('test' in response_data['username'])


class GetTestUsersTestCase(ViewTestCase):

    def test_invalid_auth(self):
        response = self.client.get('/api/v1/users/test-users/', HTTP_AUTHORIZATION=self.invalid_auth)

        self.assertEqual(401, response.status_code)

    def test_success(self):
        User.objects.create(username='test-1', is_test=True)

        response = self.client.get('/api/v1/users/test-users/', HTTP_AUTHORIZATION=self.valid_auth)

        self.assertEqual(200, response.status_code)
        response_data = json.loads(response.content)
        self.assertEqual('test-1', response_data[0]['username'])


def random_uuid():
    return '2e81fb58-f191-4c0e-aaa9-a41c92f689fa'
