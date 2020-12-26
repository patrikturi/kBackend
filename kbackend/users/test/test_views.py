import json
from unittest.mock import Mock

from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser
from django.test import override_settings
from ratelimit.exceptions import Ratelimited
from rest_framework.exceptions import AuthenticationFailed, ValidationError

from core.test.testhelpers import TestCase
from users.models import User, UserDetails
from users.views import PasswordResetView, LoginView, LogoutView, UserSearchview


class PasswordResetIntegrationTest(TestCase):

    def setUp(self):
        super().setUp()

    def test_with_nonexistent_user(self):
        response = self.client.post('/api/v1/users/reset-password/',
                                    {'username': 'JohN SmiTh', 'email': 'john@gmail.com', 'uuid': self.dummy_uuid}, HTTP_AUTHORIZATION=self.valid_auth)

        self.assertEqual(200, response.status_code)
        self.assertTrue('password' in response.data)

        user = authenticate(username='john.smith', password=response.data['password'])
        self.assertIsNotNone(user)
        self.assertEqual('john@gmail.com', user.email)
        self.assertEqual('JohN SmiTh', user.display_name)


class PasswordResetTest(TestCase):

    def setUp(self):
        super().setUp()
        self.view = PasswordResetView
        self.nanoid_mock = self.patch('users.views.nanoid')
        self.User_mock = self.patch('users.views.User')
        self.logger_mock = self.patch('users.views.logger')

    def test_success(self):

        self.nanoid_mock.generate.return_value = 'password'
        self.User_mock.reset_password.return_value = Mock(), True

        uuid = self.dummy_uuid
        response = self.view.reset_password({'username': 'JohN SmiTh', 'email': 'john@gmail.com', 'uuid': uuid})

        self.User_mock.reset_password.assert_called_once_with('john.smith', 'JohN SmiTh', 'john@gmail.com', uuid, 'password')

        self.logger_mock.info.assert_called_once()

        self.assertEqual(200, response.status_code)

    def test_with_resident_user(self):

        self.nanoid_mock.generate.return_value = 'password'
        self.User_mock.reset_password.return_value = Mock(), True

        uuid = self.dummy_uuid
        response = self.view.reset_password({'username': 'John Resident', 'email': 'john@gmail.com', 'uuid': uuid})

        self.User_mock.reset_password.assert_called_once_with('john', 'John', 'john@gmail.com', uuid, 'password')

        self.assertEqual(200, response.status_code)

    def test_with_failed_password_reset(self):

        self.nanoid_mock.generate.return_value = 'password'
        self.User_mock.reset_password.side_effect = ValidationError

        uuid = self.dummy_uuid
        self.assertRaises(ValidationError, lambda: self.view.reset_password({'username': 'John Resident', 'email': 'john@gmail.com', 'uuid': uuid}))

        self.logger_mock.info.assert_called_once()


class LoginIntegrationTest(TestCase):

    def setUp(self):
        super().setUp()
        username = 'bobby.marley'
        self.password = 'Thepassword123'
        User.objects.create_user(username, display_name='Bobby Marley', uuid=self.dummy_uuid, password=self.password)

    def test_success(self):

        response = self.client.post('/api/v1/users/login/', {'username': 'Bobby Marley', 'password': self.password})

        self.assertEqual(200, response.status_code)
        self.assertIsNotNone(response.cookies.get('sessionid'))
        response_data = json.loads(response.content)
        self.assertTrue('id' in response_data)
        self.assertEqual('Bobby Marley', response_data['display_name'])
        self.assertIsNotNone(response_data.get('csrftoken'))

    def test_with_wrong_password(self):
        response = self.client.post('/api/v1/users/login/', {'username': 'Bobby Marley', 'password': 'wrong-password'})

        self.assertEqual(401, response.status_code)
        self.assertIsNone(response.cookies.get('sessionid'))


class LoginTest(TestCase):

    def setUp(self):
        super().setUp()
        self.view = LoginView()
        self.user = User.objects.create()

        self.authenticate_mock = self.patch('users.views.authenticate')
        self.request_mock = Mock(META={'CSRF_COOKIE': 'abcd', 'REMOTE_ADDR': '127.0.0.1'})
        self.patch('users.views.login')

    def test_success(self):
        self.authenticate_mock.return_value = self.user

        response = self.view.login(self.request_mock, AnonymousUser(), {'username': 'Bobby Marley', 'password': 'dummy password'})

        self.assertEqual(200, response.status_code)

    def test_ratelimited(self):
        with override_settings(RATELIMIT_ENABLE=True):
            self.authenticate_mock.return_value = None
            for i in range(11):
                self.assertRaises(
                    AuthenticationFailed,
                    lambda: self.view.login(self.request_mock, AnonymousUser(), {'username': 'Bobby Marley', 'password': 'dummy password'})
                )

            self.authenticate_mock.return_value = self.user
            self.assertRaises(
                Ratelimited,
                lambda: self.view.login(self.request_mock, AnonymousUser(), {'username': 'Bobby Marley', 'password': 'dummy password'})
            )


class LogoutTest(TestCase):

    def setUp(self):
        super().setUp()
        self.view = LogoutView()
        self.logout_mock = self.patch('users.views.logout')
        self.logger_mock = self.patch('users.views.logger')

    def test_success(self):
        request_mock = Mock(user=Mock(is_authenticated=True))

        response = self.view.get(request_mock)

        self.logout_mock.assert_called_once_with(request_mock)
        self.logger_mock.info.assert_called_once()

        self.assertEqual(200, response.status_code)

    def test_already_logged_out(self):
        request_mock = Mock(user=Mock(is_authenticated=False))

        response = self.view.get(request_mock)

        self.logout_mock.assert_called_once()
        self.logger_mock.info.assert_not_called()

        self.assertEqual(200, response.status_code)


class UserSearchTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.view = UserSearchview

    def test_success(self):
        User.objects.create_user('bobby.marley', uuid=self.dummy_uuid, password='abcd')
        User.objects.create_user('john.smith', uuid=self.dummy_uuid, password='abcdef')
        User.objects.create_user('big.bobman', uuid=self.dummy_uuid, password='abcdef')

        response = self.client.get('/api/v1/users/search/?username=bob')

        self.assertEqual(200, response.status_code)

        usernames = [user['username'] for user in response.data]
        self.assertEqual(set(['bobby.marley', 'big.bobman']), set(usernames))

    def test_with_full_name(self):
        User.objects.create_user('bobby.marley', uuid=self.dummy_uuid, password='abcd')
        User.objects.create_user('john.smith', uuid=self.dummy_uuid, password='abcdef')
        User.objects.create_user('big.bobman', uuid=self.dummy_uuid, password='abcdef')

        response = self.view.search({'username': 'Bobby M'})

        self.assertEqual(200, response.status_code)

        usernames = [user['username'] for user in response.data]
        self.assertEqual(['bobby.marley'], usernames)

    def test_with_no_results(self):
        User.objects.create_user('john.smith', uuid=self.dummy_uuid, password='abcd')

        response = self.view.search({'username': 'bob'})

        self.assertEqual(200, response.status_code)
        self.assertEqual([], response.data)

    def test_with_too_short_username(self):
        self.assertRaises(ValidationError, lambda: self.view.search({'username': 'b'}))

    def test_with_username_not_provided(self):
        self.assertRaises(ValidationError, lambda: self.view.search({}))


class PlayerMarketplaceTestCase(TestCase):

    def test_success(self):
        User.objects.create_user('bobby.marley', available_for_transfer=False, uuid=self.dummy_uuid, password='abcd')
        User.objects.create_user('john.smith', available_for_transfer=True, uuid=self.dummy_uuid, password='abcdef')
        User.objects.create_user('big.bobman', available_for_transfer=False, uuid=self.dummy_uuid, password='abcdef')
        User.objects.create_user('newplayer', available_for_transfer=True, uuid=self.dummy_uuid, password='abcdef')

        response = self.client.get('/api/v1/users/marketplace/')

        self.assertEqual(200, response.status_code)

        usernames = [user['username'] for user in response.data]
        self.assertEqual(set(['john.smith', 'newplayer']), set(usernames))


class GetUserProfileTestCase(TestCase):

    def test_success(self):
        User.objects.create_user('bobby.marley', uuid=self.dummy_uuid, password='abcd')
        user = User.objects.create_user('john.smith', uuid=self.dummy_uuid, password='abcdef')
        User.objects.create_user('big.bobman', uuid=self.dummy_uuid, password='abcdef')

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
        self.user1 = User.objects.create_user('bobby.marley', uuid=self.dummy_uuid, password='abcd')
        self.user2 = User.objects.create_user('john.smith', uuid=self.dummy_uuid, password='abcdef')

    def test_success(self):
        self.client.force_login(self.user1)

        response = self.client.patch(f'/api/v1/users/profile/{self.user1.id}/', {'introduction': "Hi, I'm Bob!"}, content_type='application/json')

        self.assertEqual(200, response.status_code)
        self.user1.refresh_from_db()
        self.assertEqual("Hi, I'm Bob!", self.user1.introduction)
        response_data = json.loads(response.content)
        self.assertEqual("Hi, I'm Bob!", response_data['introduction'])

    def test_not_logged_in(self):
        response = self.client.patch(f'/api/v1/users/profile/{self.user1.id}/', {'introduction': "Hi, I'm Bob!"}, content_type='application/json')

        self.assertEqual(401, response.status_code)

    def test_create_userdetails(self):
        self.client.force_login(self.user1)

        response = self.client.patch(f'/api/v1/users/profile/{self.user1.id}/', {'introduction': "Hi, I'm Bob!", 'user_details': {'biography': 'My Bio'}}, content_type='application/json')

        self.assertEqual(200, response.status_code)
        user_details = UserDetails.objects.get(user=self.user1)
        self.assertEqual('My Bio', user_details.biography)

        response_data = json.loads(response.content)
        self.assertEqual('My Bio', response_data['user_details']['biography'])

    def test_update_userdetails(self):
        self.client.force_login(self.user1)
        user_details = UserDetails.objects.create(user=self.user1, biography='Original Bio')

        response = self.client.patch(f'/api/v1/users/profile/{self.user1.id}/', {'introduction': "Hi, I'm Bob!", 'user_details': {'biography': 'My Bio'}}, content_type='application/json')

        self.assertEqual(200, response.status_code)
        user_details.refresh_from_db()
        self.assertEqual('My Bio', user_details.biography)

        response_data = json.loads(response.content)
        self.assertEqual('My Bio', response_data['user_details']['biography'])

    def test_with_different_user(self):
        self.client.force_login(self.user2)

        response = self.client.patch(f'/api/v1/users/profile/{self.user1.id}/', {'introduction': "Hi, I'm Bob!"}, content_type='application/json')

        self.assertEqual(403, response.status_code)


class GePrivatetUserProfileTestCase(TestCase):

    def test_success(self):
        User.objects.create_user('bobby.marley', uuid=self.dummy_uuid, password='abcd')
        user = User.objects.create_user('john.smith', uuid=self.dummy_uuid, password='abcdef')
        User.objects.create_user('big.bobman', uuid=self.dummy_uuid, password='abcdef')

        UserDetails.objects.create(user=user, biography='This is my bio.')

        self.client.force_login(user)

        response = self.client.get('/api/v1/users/me/profile/')

        self.assertEqual(200, response.status_code)
        self.assertEqual('john.smith', response.data['username'])
        self.assertEqual('This is my bio.', response.data['user_details'][0]['biography'])


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


class ChangePasswordTestCase(TestCase):

    def test_success(self):
        user = User.objects.create_user('bobby', uuid=self.dummy_uuid, password='old-password')
        self.client.force_login(user)

        response = self.client.post('/api/v1/users/change-password/', {'old_password': 'old-password', 'new_password': 'new-password'})

        self.assertEqual(200, response.status_code)
        self.client.logout()
        self.assertTrue(self.client.login(username='bobby', password='new-password'))

    def test_wrong_password(self):
        user = User.objects.create_user('bobby', uuid=self.dummy_uuid, password='old-password')
        self.client.force_login(user)

        response = self.client.post('/api/v1/users/change-password/', {'old_password': 'wrong-password', 'new_password': 'new-password'})

        self.assertEqual(403, response.status_code)
        self.client.logout()
        self.assertFalse(self.client.login(username='bobby', password='new-password'))
