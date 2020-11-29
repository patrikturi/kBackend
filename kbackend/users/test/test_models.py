from django.contrib.auth import authenticate
from core.test.testhelpers import TestCase
from users.models import User
from rest_framework.exceptions import ValidationError, PermissionDenied


class GetOrCreateUserTestCase(TestCase):

    def test_get_existing(self):
        existing_user = User.objects.create_user('john.smith', password='existing-password')

        user = User.get_or_create('John Smith')

        self.assertEqual(existing_user.id, user.id)
        self.assertTrue(user.is_active)

    def test_new(self):
        user = User.get_or_create('John SmiTH')

        self.assertEqual('john.smith', user.username)
        self.assertFalse(user.is_active)
        self.assertEqual('John SmiTH', user.display_name)

    def test_invalid_name(self):
        self.assertRaises(ValidationError, lambda: User.get_or_create('john.smith'))


class BulkGetOrCreateTestCase(TestCase):

    def test_no_existing_user(self):
        users = User.bulk_get_or_create(['John Sonmez', 'Johnny Resident'])

        usernames = [user.username for user in users]
        display_names = [user.display_name for user in users]
        self.assertEqual(set(['john.sonmez', 'johnny']), set(usernames))
        self.assertEqual(set(['John Sonmez', 'Johnny']), set(display_names))

    def test_all_users_exist(self):
        User.objects.create(username='usera')
        User.objects.create(username='userb')

        users = User.bulk_get_or_create(['userA Resident', 'userB Resident'])

        usernames = [user.username for user in users]
        self.assertEqual(set(['usera', 'userb']), set(usernames))

    def test_some_users_exist(self):
        User.objects.create(username='userb')

        users = User.bulk_get_or_create(['userA Resident', 'userB Resident', 'userC Resident'])

        usernames = [user.username for user in users]
        self.assertEqual(set(['usera', 'userb', 'userc']), set(usernames))


class BulkAddMatchTestCase(TestCase):

    def test_success(self):
        users = User.bulk_get_or_create(['John Sonmez', 'Johnny Resident'])
        users[1].matches = 3
        users[1].save()

        User.bulk_add_match(users)

        users[0].refresh_from_db()
        users[1].refresh_from_db()
        self.assertEqual(1, users[0].matches)
        self.assertEqual(4, users[1].matches)


class ChangePasswordTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.user = User.objects.create(username='user1')
        self.user.set_password('orig-password')
        self.user.save()

    def test_success(self):
        self.user.change_password('orig-password', 'new-password')

        auth_user = authenticate(username='user1', password='new-password')
        self.assertIsNotNone(auth_user)

    def test_with_invalid_old_password(self):
        self.assertRaises(PermissionDenied, lambda: self.user.change_password('invalid-password', 'new-password'))

        auth_user = authenticate(username='user1', password='new-password')
        self.assertIsNone(auth_user)

    def test_with_empty_new_password(self):
        self.assertRaises(ValidationError, lambda: self.user.change_password('orig-password', ''))

        auth_user = authenticate(username='user1', password='orig-password')
        self.assertIsNotNone(auth_user)


class AddStatTest(TestCase):

    def setUp(self):
        super().setUp()
        self.user = self.user = User.objects.create(username='user1')

    def test_add_coints(self):
        self.user.add_stat('kcoins', 2)

        self.user.refresh_from_db()
        self.assertEqual(2, self.user.kcoins)

    def test_add_goal(self):
        self.user.add_stat('goal', 1)

        self.user.refresh_from_db()
        self.assertEqual(1, self.user.goals)

    def test_add_assist(self):
        self.user.add_stat('assist', 1)

        self.user.refresh_from_db()
        self.assertEqual(1, self.user.assists)

    def test_add_stat_not_cached(self):
        self.user.add_stat('red', 1)

    def test_not_existing_stat(self):
        self.assertRaises(KeyError, lambda: self.user.add_stat('non-existent-stat', 1))


class ResetPasswordTest(TestCase):

    def test_with_nonexistent_user(self):
        User.reset_password('john.smith', 'JohN SmiTh', 'john@gmail.com', self.dummy_uuid, 'some-password')

        user = authenticate(username='john.smith', password='some-password')
        self.assertIsNotNone(user)

    def test_with_existing_user(self):
        User.objects.create_user('john.smith', password='existing-password', is_staff=False)

        User.reset_password('john.smith', 'JohN SmiTh', 'john@gmail.com', self.dummy_uuid, 'new-password')

        user = authenticate(username='john.smith', password='new-password')
        self.assertIsNotNone(user)

    def test_with_staff_user(self):
        User.objects.create_user('john.smith', password='existing-password', is_staff=True)

        self.assertRaises(PermissionDenied, lambda: User.reset_password('john.smith', 'JohN SmiTh', 'john@gmail.com', self.dummy_uuid, 'new-password'))
