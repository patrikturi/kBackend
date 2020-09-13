from unittest.mock import patch, Mock

from django.test import TestCase

from soccer.helpers import create_stat
from soccer.models import SoccerStat, MatchParticipation
from users.models import User
from soccer.helpers import perform_create_stat, create_match_with_users


class PerformCreateStatTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.user = User.objects.create(username='user')

    @patch('soccer.helpers.create_stat')
    def test_missing_username(self, create_stat_mock):
        create_stat_mock.return_value = None, False

        incomplete_data = {'dummy-key': 'dummy-value'}
        response = perform_create_stat(incomplete_data)

        self.assertEqual(400, response.status_code)

    @patch('soccer.helpers.create_stat')
    def test_success(self, create_stat_mock):
        create_stat_mock.return_value = Mock(), True

        dummy_data = {'username': 'some.user', 'dummy-key': 'dummy-value'}
        response = perform_create_stat(dummy_data)

        self.assertEqual(201, response.status_code)

    @patch('soccer.helpers.create_stat')
    def test_stat_already_exists(self, create_stat_mock):
        create_stat_mock.return_value = Mock(), False

        incomplete_data = {'dummy-key': 'dummy-value'}
        response = perform_create_stat(incomplete_data)

        self.assertEqual(200, response.status_code)


class CreateStatTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.user = User.objects.create(username='user')

    @patch('soccer.helpers.User')
    def test_with_no_user_specified(self, User_mock):
        User_mock.get_or_create.side_effect = Exception()

        valid_data = {'stat_uuid':'some-uuid', 'stat_type': 'goal', 'value': 1}
        stat, created = create_stat(None, valid_data)

        self.assertIsNone(stat)
        self.assertFalse(created)

    @patch('soccer.helpers.User')
    def test_with_missing_uuid(self, User_mock):
        User_mock.get_or_create.return_value = self.user

        incomplete_data = {'stat_type': 'goal', 'value': 1}
        stat, created = create_stat('user', incomplete_data)

        self.assertIsNone(stat)
        self.assertFalse(created)

    @patch('soccer.helpers.User')
    def test_with_missing_type(self, User_mock):
        User_mock.get_or_create.return_value = self.user

        incomplete_data = {'stat_uuid':'some-uuid', 'value': 1}
        stat, created = create_stat('user', incomplete_data)

        self.assertIsNone(stat)
        self.assertFalse(created)

    @patch('soccer.helpers.User')
    def test_with_nonexistent_stat(self, User_mock):
        User_mock.get_or_create.return_value = self.user

        valid_data = {'stat_uuid':'some-uuid', 'stat_type': 'goal', 'value': 1}
        stat, created = create_stat('user', valid_data)

        self.assertIsNotNone(stat)
        self.assertTrue(created)
        self.assertEqual(1, self.user.goals)

    @patch('soccer.helpers.User')
    def test_with_existing_stat(self, User_mock):
        User_mock.get_or_create.return_value = self.user

        existing_stat = SoccerStat.objects.create(user=self.user, stat_uuid='some-uuid', stat_type='assist', value=1)

        valid_data = {'stat_uuid':'some-uuid', 'stat_type': 'assist', 'value': 1}
        stat, created = create_stat('user', valid_data)

        self.assertIsNotNone(stat)
        self.assertFalse(created)
        self.assertEqual(0, self.user.goals)


class CreateMatchTestCase(TestCase):

    def test_create_success(self):
        user1 = User.objects.create(username='user-1')
        user2 = User.objects.create(username='user-2')
        user3 = User.objects.create(username='user-3')
        user4 = User.objects.create(username='user-4')

        match = create_match_with_users('Mini League', 'Team A', 'Team B', [user1, user2], [user3, user4])

        self.assertEqual(1, match.id)

        part_home = MatchParticipation.objects.filter(match=match, side='home')
        part_away = MatchParticipation.objects.filter(match=match, side='away')
        home_names = [part.user.username for part in part_home]
        away_names = [part.user.username for part in part_away]

        self.assertEqual(['user-1', 'user-2'], home_names)
        self.assertEqual(['user-3', 'user-4'], away_names)
