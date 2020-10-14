from users.models import User
from rest_framework.exceptions import ValidationError


def get_test_users():
    test_users = User.objects.filter(is_test=True).order_by('id').all()
    return list(test_users[:200])


def normalize_display_name(display_name):
    if display_name and '.' in display_name:
        raise ValidationError('Expected Legacy Name instead of Username')
    return display_name.rsplit('Resident', maxsplit=1)[0].strip() if display_name else display_name


def to_username(display_name):
    return display_name.lower().replace(' ', '.') if display_name else display_name
