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
