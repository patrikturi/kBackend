import json
from unittest.mock import Mock

from django.contrib.auth import authenticate
from django.test import override_settings, tag
from rest_framework.exceptions import ValidationError

from core.test.testhelpers import TestCase
from users.models import User, UserDetails
from users.views import PasswordResetView


class PasswordResetIntegrationTest(TestCase):

    def setUp(self):
        super().setUp()

    def test_with_nonexistent_user(self):
        response = self.client.post('/api/v1/users/reset-password/',
                                    {'username': 'JohN SmiTh', 'email': 'john@gmail.com', 'uuid': random_uuid()}, HTTP_AUTHORIZATION=self.valid_auth)

        self.assertEqual(200, response.status_code)
        self.assertTrue('password' in response.data)

        user = authenticate(username='john.smith', password=response.data['password'])
        self.assertIsNotNone(user)
        self.assertEqual('john@gmail.com', user.email)
        self.assertEqual('JohN SmiTh', user.display_name)


class PasswordResetTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.view = PasswordResetView
        self.nanoid_mock = self.patch('users.views.nanoid')
        self.User_mock = self.patch('users.views.User')
        self.logger_mock = self.patch('users.views.logger')

    def test_success(self):

        self.nanoid_mock.generate.return_value = 'password'
        self.User_mock.reset_password.return_value = Mock(), True

        uuid = random_uuid()
        response = self.view.reset_password({'username': 'JohN SmiTh', 'email': 'john@gmail.com', 'uuid': uuid})

        self.User_mock.reset_password.assert_called_once_with('john.smith', 'JohN SmiTh', 'john@gmail.com', uuid, 'password')

        self.logger_mock.info.assert_called_once()

        self.assertEqual(200, response.status_code)

    def test_with_resident_user(self):

        self.nanoid_mock.generate.return_value = 'password'
        self.User_mock.reset_password.return_value = Mock(), True

        uuid = random_uuid()
        response = self.view.reset_password({'username': 'John Resident', 'email': 'john@gmail.com', 'uuid': uuid})

        self.User_mock.reset_password.assert_called_once_with('john', 'John', 'john@gmail.com', uuid, 'password')

        self.assertEqual(200, response.status_code)

    def test_with_failed_password_reset(self):

        self.nanoid_mock.generate.return_value = 'password'
        self.User_mock.reset_password.side_effect = ValidationError

        uuid = random_uuid()
        self.assertRaises(ValidationError, lambda: self.view.reset_password({'username': 'John Resident', 'email': 'john@gmail.com', 'uuid': uuid}))

        self.logger_mock.info.assert_called_once()


class LoginTestCase(TestCase):

    def setUp(self):
        super().setUp()
        username = 'bobby.marley'
        self.password = 'Thepassword123'
        User.objects.create_user(username, display_name='Bobby Marley', uuid=random_uuid(), password=self.password)

    def test_success(self):

        response = self.client.post('/api/v1/users/login/', {'username': 'Bobby Marley', 'password': self.password})

        self.assertEqual(200, response.status_code)
        self.assertIsNotNone(response.cookies.get('sessionid'))
        response_data = json.loads(response.content)
        self.assertTrue(isinstance(response_data['id'], int))
        self.assertEqual('Bobby Marley', response_data['display_name'])
        self.assertIsNotNone(response_data.get('csrftoken'))

    def test_with_wrong_password(self):
        response = self.client.post('/api/v1/users/login/', {'username': 'Bobby Marley', 'password': 'wrong-password'})

        self.assertEqual(401, response.status_code)
        self.assertIsNone(response.cookies.get('sessionid'))

    @tag('slow')
    def test_ratelimited(self):
        with override_settings(RATELIMIT_ENABLE=True):
            for i in range(11):
                self.client.post('/api/v1/users/login/', {'username': 'Bobby Marley', 'password': 'wrong-password'})

            response = self.client.post('/api/v1/users/login/', {'username': 'Bobby Marley', 'password': self.password})
            self.assertEqual(429, response.status_code)


class AdminTestCase(TestCase):

    @tag('slow')
    def test_ratelimited(self):
        with override_settings(RATELIMIT_ENABLE=True):
            for i in range(11):
                self.client.post('/adminsite/login/', {'username': 'admin', 'password': '1234'})

            response = self.client.post('/adminsite/login/', {'username': 'admin', 'password': '1234'})
            self.assertEqual(429, response.status_code)


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

        response = self.client.get(f'/api/v1/users/profile/{user.id}/')

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

        response = self.client.patch(f'/api/v1/users/profile/{self.user1.id}/', {'introduction': "Hi, I'm Bob!"}, content_type='application/json')

        self.assertEqual(200, response.status_code)
        self.user1.refresh_from_db()
        self.assertEqual("Hi, I'm Bob!", self.user1.introduction)
        response_data = json.loads(response.content)
        self.assertEqual("Hi, I'm Bob!", response_data['introduction'])

    def test_create_userdetails(self):
        self.client.force_login(self.user1)

        response = self.client.patch(f'/api/v1/users/profile/{self.user1.id}/', {'introduction': "Hi, I'm Bob!", 'user_details': {'biography': 'My Bio'}}, content_type='application/json')

        self.assertEqual(200, response.status_code)
        user_details = UserDetails.objects.get(user=self.user1)
        self.assertEqual('My Bio', user_details.biography)

    def test_update_userdetails(self):
        self.client.force_login(self.user1)
        user_details = UserDetails.objects.create(user=self.user1, biography='Original Bio')

        response = self.client.patch(f'/api/v1/users/profile/{self.user1.id}/', {'introduction': "Hi, I'm Bob!", 'user_details': {'biography': 'My Bio'}}, content_type='application/json')

        self.assertEqual(200, response.status_code)
        user_details.refresh_from_db()
        self.assertEqual('My Bio', user_details.biography)

    def test_with_different_user(self):
        self.client.force_login(self.user2)

        response = self.client.patch(f'/api/v1/users/profile/{self.user1.id}/', {'introduction': "Hi, I'm Bob!"}, content_type='application/json')

        self.assertEqual(403, response.status_code)

    def test_not_logged_in(self):
        response = self.client.patch(f'/api/v1/users/profile/{self.user1.id}/', {'introduction': "Hi, I'm Bob!"}, content_type='application/json')

        self.assertEqual(401, response.status_code)


class GePrivatetUserProfileTestCase(TestCase):

    def test_success(self):
        User.objects.create_user('bobby.marley', uuid=random_uuid(), password='abcd')
        user = User.objects.create_user('john.smith', uuid=random_uuid(), password='abcdef')
        User.objects.create_user('big.bobman', uuid=random_uuid(), password='abcdef')

        UserDetails.objects.create(user=user, biography='This is my bio.')

        self.client.force_login(user)

        response = self.client.get('/api/v1/users/me/profile/')

        self.assertEqual(200, response.status_code)
        self.assertEqual('john.smith', response.data['username'])
        self.assertEqual('This is my bio.', response.data['user_details'][0]['biography'])

    def test_not_logged_in(self):
        response = self.client.get('/api/v1/users/me/profile/')

        self.assertEqual(401, response.status_code)


class CreateTestUserTestCase(TestCase):

    def test_success(self):
        response = self.client.post('/api/v1/users/test-users/', HTTP_AUTHORIZATION=self.valid_auth)

        self.assertEqual(200, response.status_code)
        response_data = json.loads(response.content)
        self.assertTrue('test' in response_data['username'])


class GetTestUsersTestCase(TestCase):

    def test_success(self):
        User.objects.create(username='test-1', is_test=True)

        response = self.client.get('/api/v1/users/test-users/', HTTP_AUTHORIZATION=self.valid_auth)

        self.assertEqual(200, response.status_code)
        response_data = json.loads(response.content)
        self.assertEqual('test-1', response_data[0]['username'])


def random_uuid():
    return '2e81fb58-f191-4c0e-aaa9-a41c92f689fa'
