from django.test import TestCase
from users.models import User
from rest_framework.exceptions import ValidationError


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
