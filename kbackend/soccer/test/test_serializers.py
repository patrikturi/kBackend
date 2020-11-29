from django.test import TestCase
from rest_framework.exceptions import ValidationError

from soccer.serializers import SoccerStatCreateSerializer, MatchCreateSerializer

from users.models import User
from soccer.models import SoccerStat


class SoccerStatCreateSerializerTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='Joe')

    def test_success(self):
        valid_data = {'user': self.user.id, 'stat_type': 'kcoins', 'value': 1, 'stat_uuid': 'some-uuid'}
        serializer = SoccerStatCreateSerializer(data=valid_data)
        stat, created = serializer.get_or_create()

        stat.refresh_from_db()
        self.assertTrue(created)
        self.assertEqual('some-uuid', stat.stat_uuid)

    def test_with_existing_uuid(self):
        existing_uuid = 'test-uuid'
        existing_stat = SoccerStat.objects.create(user=self.user, stat_uuid=existing_uuid, stat_type='kcoins', value=5)

        valid_data = {'user': self.user.id, 'stat_type': 'kcoins', 'value': 10, 'stat_uuid': existing_uuid}
        serializer = SoccerStatCreateSerializer(data=valid_data)
        stat, created = serializer.get_or_create()

        self.assertFalse(created)
        self.assertEqual(existing_stat.id, stat.id)
        self.assertEqual(existing_uuid, stat.stat_uuid)

    def test_with_invalid_Data(self):
        invalid_data = {'user': self.user.id, 'stat_type': 'invalid', 'value': 1, 'stat_uuid': 'some-uuid'}
        serializer = SoccerStatCreateSerializer(data=invalid_data)
        self.assertRaises(ValidationError, lambda: serializer.get_or_create())


class CreateMatchSerializerTest(TestCase):

    def setUp(self):
        super().setUp()

    def test_success(self):
        valid_data = {'competition': 'comp', 'home_team': 'a', 'away_team': 'b', 'home_players': ['user1', 'user2'], 'away_players': ['user3', 'user4']}
        serializer = MatchCreateSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_user_in_both_teams(self):
        invalid_data = {'competition': 'comp', 'home_team': 'a', 'away_team': 'b', 'home_players': ['user1', 'user2'], 'away_players': ['user2', 'user3']}
        serializer = MatchCreateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())

    def test_away_players_missing(self):
        invalid_data = {'competition': 'comp', 'home_team': 'a', 'away_team': 'b', 'home_players': ['user1', 'user2']}
        serializer = MatchCreateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
