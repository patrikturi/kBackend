from django.test import TestCase

from users.models import User
from users.helpers import get_test_users


class GetTestUsersTestCase(TestCase):

    def test_no_users(self):
        users = get_test_users()

        self.assertEqual([], users)

    def test_success(self):
        User.objects.create(username='test-a', is_test=True)
        User.objects.create(username='user-1', is_test=False)
        User.objects.create(username='test-b', is_test=True)
        User.objects.create(username='user-2', is_test=False)

        users = get_test_users()

        usernames = [user.username for user in users]
        self.assertEqual(['test-a', 'test-b'], usernames)
