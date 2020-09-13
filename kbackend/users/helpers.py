from users.models import User


def get_test_users():
    test_users = User.objects.filter(is_test=True).order_by('id').all()
    return list(test_users[:200])
