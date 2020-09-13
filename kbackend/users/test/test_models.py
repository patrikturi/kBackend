from django.test import TestCase
from users.models import User


class GetOrCreateUserTestCase(TestCase):

    def test_get_existing(self):
        existing_user = User.objects.create_user('john.smith', password='existing-password')

        user = User.get_or_create('john.smith')

        self.assertEqual(existing_user.id, user.id)
        self.assertTrue(user.is_active)

    def test_new(self):
        user = User.get_or_create('john.smith')

        self.assertEqual('john.smith', user.username)
        self.assertFalse(user.is_active)


class BulkGetOrCreateTestCase(TestCase):

    def test_no_existing_user(self):
        users = User.bulk_get_or_create(['userA', 'userB'])

        usernames = [user.username for user in users]
        self.assertEqual(set(['userA', 'userB']), set(usernames))

    def test_all_users_exist(self):
        User.objects.create(username='userA')
        User.objects.create(username='userB')

        users = User.bulk_get_or_create(['userA', 'userB'])

        usernames = [user.username for user in users]
        self.assertEqual(set(['userA', 'userB']), set(usernames))

    def test_some_users_exist(self):
        User.objects.create(username='userB')

        users = User.bulk_get_or_create(['userA', 'userB', 'userC'])

        usernames = [user.username for user in users]
        self.assertEqual(set(['userA', 'userB', 'userC']), set(usernames))
