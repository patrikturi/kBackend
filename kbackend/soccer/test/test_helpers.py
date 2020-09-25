from unittest.mock import patch, Mock

from django.test import TestCase

from soccer.helpers import create_stat
from soccer.models import SoccerStat, MatchParticipation
from users.models import User
from soccer.helpers import perform_create_stat, perform_create_match
from rest_framework.exceptions import ValidationError


class PerformCreateStatTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.user = User.objects.create(username='user')

    @patch('soccer.helpers.create_stat')
    def test_missing_username(self, create_stat_mock):
        create_stat_mock.side_effect = ValidationError()

        incomplete_data = {'dummy-key': 'dummy-value'}
        self.assertRaises(ValidationError, lambda: perform_create_stat(incomplete_data))

    @patch('soccer.helpers.create_stat')
    def test_success(self, create_stat_mock):
        create_stat_mock.return_value = Mock(), True

        dummy_data = {'username': 'some.user', 'dummy-key': 'dummy-value'}
        created = perform_create_stat(dummy_data)

        self.assertTrue(created)

    @patch('soccer.helpers.create_stat')
    def test_stat_already_exists(self, create_stat_mock):
        create_stat_mock.return_value = Mock(), False

        incomplete_data = {'dummy-key': 'dummy-value'}
        created = perform_create_stat(incomplete_data)

        self.assertFalse(created)


class CreateStatTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.user = User.objects.create(username='user')

    @patch('soccer.helpers.User')
    def test_with_no_user_specified(self, User_mock):
        User_mock.get_or_create.side_effect = Exception()

        valid_data = {'stat_uuid': 'some-uuid', 'stat_type': 'goal', 'value': 1}
        self.assertRaises(ValidationError, lambda: create_stat(None, valid_data))

    @patch('soccer.helpers.User')
    def test_with_missing_uuid(self, User_mock):
        User_mock.get_or_create.return_value = self.user

        incomplete_data = {'stat_type': 'goal', 'value': 1}
        self.assertRaises(ValidationError, lambda: create_stat('user', incomplete_data))

    @patch('soccer.helpers.User')
    def test_with_missing_type(self, User_mock):
        User_mock.get_or_create.return_value = self.user

        incomplete_data = {'stat_uuid':'some-uuid', 'value': 1}
        self.assertRaises(ValidationError, lambda: create_stat('user', incomplete_data))

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

        SoccerStat.objects.create(user=self.user, stat_uuid='some-uuid', stat_type='assist', value=1)

        valid_data = {'stat_uuid':'some-uuid', 'stat_type': 'assist', 'value': 1}
        stat, created = create_stat('user', valid_data)

        self.assertIsNotNone(stat)
        self.assertFalse(created)
        self.assertEqual(0, self.user.goals)


class PerformCreateMatchTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.user1 = User.objects.create(username='user-1')
        self.user2 = User.objects.create(username='user-2')
        self.user3 = User.objects.create(username='user-3')
        self.user4 = User.objects.create(username='user-4')

    @patch('users.models.User.bulk_get_or_create')
    def test_all_parameters(self, mock_bulk_get_or_create):
        mock_bulk_get_or_create.side_effect = [[self.user1, self.user2], [self.user3, self.user4]]

        valid_data = {'competition': 'FM', 'home_team': 'Team A', 'away_team': 'Team B', 'home_players': ['user1', 'user2'], 'away_players': ['user3', 'user4']}
        match = perform_create_match(valid_data)

        self.assertEqual('FM', match.competition_name)
        self.assertEqual('Team A', match.home_team)
        self.assertEqual('Team B', match.away_team)

        part_home = MatchParticipation.objects.filter(match=match, side='home')
        part_away = MatchParticipation.objects.filter(match=match, side='away')
        home_names = [part.user.username for part in part_home]
        away_names = [part.user.username for part in part_away]

        self.assertEqual(['user-1', 'user-2'], home_names)
        self.assertEqual(['user-3', 'user-4'], away_names)

    @patch('users.models.User.bulk_get_or_create')
    def test_mandatory_parameters(self, mock_bulk_get_or_create):
        mock_bulk_get_or_create.side_effect = [[self.user1, self.user2], [self.user3, self.user4]]

        valid_data = {'home_team': 'Team A', 'away_team': 'Team B', 'home_players': ['user1', 'user2'], 'away_players': ['user3', 'user4']}
        match = perform_create_match(valid_data)

        self.assertIsNotNone(match)

    @patch('users.models.User.bulk_get_or_create')
    def test_no_players(self, mock_bulk_get_or_create):
        mock_bulk_get_or_create.side_effect = [[self.user1, self.user2], []]

        data_players_missing = {'home_team': 'Team1', 'away_team': 'Team2', 'home_players': ['user1', 'user2'], 'away_players': []}
        self.assertRaises(ValidationError, lambda: perform_create_match(data_players_missing))

    @patch('users.models.User.bulk_get_or_create')
    def test_no_team_name(self, mock_bulk_get_or_create):
        mock_bulk_get_or_create.side_effect = [[self.user1], [self.user2]]

        data_away_team_missing = {'home_team': 'Team1', 'home_players': ['user1'], 'away_players': ['user2']}
        self.assertRaises(ValidationError, lambda: perform_create_match(data_away_team_missing))

    @patch('users.models.User.bulk_get_or_create')
    def test_player_in_both_teams(self, mock_bulk_get_or_create):
        mock_bulk_get_or_create.side_effect = [[self.user1, self.user2], [self.user3, self.user2]]

        valid_data = {'home_team': 'Team A', 'away_team': 'Team B', 'home_players': ['user1', 'user2'], 'away_players': ['user3', 'user2']}
        self.assertRaises(ValidationError, lambda: perform_create_match(valid_data))
