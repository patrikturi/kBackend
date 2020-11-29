import json
from unittest.mock import Mock, patch, DEFAULT, call

from rest_framework.exceptions import ValidationError

from core.test.testhelpers import TestCase
from soccer.views import MatchesView, SoccerStatsView
from users.models import User


class CreateStatIntegrationTest(TestCase):

    def test_success(self):
        User.objects.create(username='user')

        valid_data = {'username': 'user', 'stat_uuid': 'someuuid', 'stat_type': 'goal', 'value': 1}
        response = self.client.post('/api/v1/soccer/stats/', valid_data,
                                    HTTP_AUTHORIZATION=self.valid_auth, content_type='application/json')

        self.assertEqual(201, response.status_code)


class CreateStatTestCase(TestCase):

    def using(self, context_manager):
        enter_value = context_manager.__enter__()
        self.addCleanup(context_manager.__exit__)
        return enter_value

    def patch(self, target, new=DEFAULT, spec=None, create=False, mocksignature=False, spec_set=None, autospec=False, new_callable=None, **kwargs):
        return self.using(patch(target=target, new=new, spec=spec, create=create, mocksignature=mocksignature, spec_set=spec_set, autospec=autospec, new_callable=new_callable, **kwargs))

    def setUp(self):
        super().setUp()
        self.view = SoccerStatsView
        self.basic_user = Mock(username='user')

        self.user_mock = Mock(id=12)
        self.User_mock = self.patch('soccer.views.User')
        self.User_mock.get_or_create.return_value = self.user_mock

        self.serializer_class_mock = self.patch('soccer.views.SoccerStatCreateSerializer')
        self.serializer_mock = Mock()
        self.serializer_class_mock.return_value = self.serializer_mock

        self.logger_mock = self.patch('soccer.views.logger')

    def test_success(self):
        self.serializer_mock.get_or_create.return_value = Mock(), True

        response = self.view.create_stat(self.basic_user, {'username': 'some.user', 'stat_type': 'dummy_type', 'value': 1})

        self.assertEqual(201, response.status_code)
        self.User_mock.get_or_create.assert_called_once_with('some.user')
        self.serializer_class_mock.assert_called_once_with(data={'user': 12, 'stat_type': 'dummy_type', 'value': 1})
        self.serializer_mock.get_or_create.assert_called_once()
        self.user_mock.add_stat.assert_called_once_with('dummy_type', 1)
        self.logger_mock.info.assert_called_once()

    def test_stat_already_exists(self):
        self.serializer_mock.get_or_create.return_value = Mock(), False

        response = self.view.create_stat(self.basic_user, {'username': 'some.user', 'stat_type': 'dummy_type', 'value': 1})

        self.assertEqual(200, response.status_code)
        self.User_mock.get_or_create.assert_called_once_with('some.user')
        self.serializer_mock.get_or_create.assert_called_once()
        self.user_mock.add_stat.assert_not_called()
        self.logger_mock.info.assert_called_once()

    def test_username_not_provided(self):
        self.User_mock.get_or_create.side_effect = ValidationError()

        self.assertRaises(ValidationError, lambda: self.view.create_stat(self.basic_user, {'stat_type': 'dummy_type', 'value': 1}))


class CreateMatchIntegrationTest(TestCase):

    def test_success(self):
        valid_data = {'home_team': 'Team A', 'away_team': 'Team B', 'home_players': ['userA', 'userB'], 'away_players': ['userC', 'userD']}
        response = self.client.post('/api/v1/soccer/matches/', valid_data,
                                    HTTP_AUTHORIZATION=self.valid_auth, content_type='application/json')

        self.assertEqual(201, response.status_code)
        response_data = json.loads(response.content)
        self.assertTrue(isinstance(response_data['id'], int))


class CreateMatchTest(TestCase):

    def setUp(self):
        super().setUp()
        self.view = MatchesView
        self.basic_user = Mock(username='user')

        self.serializer_mock = Mock()
        self.serializer_class_mock = self.patch('soccer.views.MatchCreateSerializer')
        self.serializer_class_mock.return_value = self.serializer_mock

        self.match_mock = Mock()
        self.Match_mock = self.patch('soccer.views.Match')
        self.Match_mock.objects.create.return_value = self.match_mock

        self.users_list1 = [Mock(username='p1')]
        self.users_list2 = [Mock(username='p2')]
        self.User_mock = self.patch('soccer.views.User')
        self.User_mock.bulk_get_or_create.side_effect = [self.users_list1, self.users_list2]

        self.MatchParticipation_mock = self.patch('soccer.views.MatchParticipation')
        self.logger_mock = self.patch('soccer.views.logger')

    def test_success(self):
        data = {'competition': 'c', 'home_team': 'teamA', 'away_team': 'teamB', 'home_players': ['p1'], 'away_players': ['p2']}

        response = self.view.create_match(self.basic_user, data)

        self.serializer_class_mock.assert_called_once_with(data=data)
        self.serializer_mock.is_valid.assert_called_once_with(raise_exception=True)

        self.Match_mock.objects.create.assert_called_once_with(competition_name='c', home_team='teamA', away_team='teamB')

        self.User_mock.bulk_get_or_create.assert_has_calls([
            call(['p1']),
            call(['p2'])
        ])

        self.MatchParticipation_mock.objects.bulk_create_team.assert_has_calls([
            call(self.match_mock, self.users_list1, side='home'),
            call(self.match_mock, self.users_list2, side='away'),
        ])

        self.User_mock.bulk_add_match.assert_called_once_with(self.users_list1 + self.users_list2)

        self.logger_mock.info.assert_called_once()

        self.assertEqual(201, response.status_code)
