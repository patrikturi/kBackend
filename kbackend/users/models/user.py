from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from rest_framework.exceptions import ValidationError


class User(AbstractUser):

    # http://wiki.secondlife.com/wiki/Category:LSL_Avatar/Name
    # http://wiki.secondlife.com/wiki/Limits
    # eg. 'john.smith' or 'john'
    username_validator = RegexValidator(r'^[a-z0-9]+\.?[a-z0-9]+$')

    username = models.CharField(
        _('username'),
        max_length=63,
        unique=True,
        help_text=_('Required. 63 characters or fewer. Only lower case english alphabet and at most one dot is allowed.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )

    display_name = models.CharField(max_length=63)

    # http://wiki.secondlife.com/wiki/UUID
    uuid_validator = RegexValidator(r'^[a-z0-9-]{36}$')

    uuid = models.CharField(max_length=36, help_text='SL uuid: string of 32 hex characters with four dashes interspersed',
                            validators=[uuid_validator], blank=True)

    is_test = models.BooleanField(default=False)

    introduction = models.CharField(max_length=255, blank=True)

    available_for_transfer = models.BooleanField(default=False)

    kcoins = models.IntegerField(default=0)
    goals = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)

    updated_at = models.DateTimeField(auto_now=True)

    # Required for admin users
    REQUIRED_FIELDS = ['email', 'uuid']

    # Remove these Django fields and derive them from the SL username
    first_name = None
    last_name = None

    @property
    def first_name(self):
        return self.username.split('.')[0].capitalize()

    @property
    def last_name(self):
        username_parts = self.username.split('.')
        if len(username_parts) < 2:
            return 'Resident'
        return username_parts[1].capitalize()

    @property
    def profile_picture_url(self):
        # For start this will do, later users could upload their own
        return f'https://my-secondlife-agni.akamaized.net/users/{self.username}/sl_image.png'

    def get_display_name(self):
        return self.get_full_name()

    def add_stat(self, stat_type, value):
        changed = False
        if stat_type == 'goal':
            self.goals += value
            changed = True
        elif stat_type == 'assist':
            self.assists += value
            changed = True
        elif stat_type == 'kcoints':
            self.kcoins += value
            changed = True

        if changed:
            self.save()

    @classmethod
    def reset_password(cls, username, email, uuid, password):
        from users.serializers import PasswordResetSerializer

        user = User.objects.filter(username=username).first()

        is_new = user is None
        if user:
            if user.uuid and user.uuid != uuid:
                raise ValidationError('uuid of the user does not match')
            user.is_active = True
            user.uuid = uuid
            user.set_password(password)
            user.save()
        else:
            serializer = PasswordResetSerializer(data={'username': username, 'email': email, 'uuid': uuid})
            serializer.is_valid(raise_exception=True)
            user = User.objects.create_user(username, email=email, uuid=uuid, password=password)
        return user, is_new

    @classmethod
    def get_or_create(cls, username):
        user = User.objects.filter(username=username).first()

        if not user:
            user = cls._create_non_registered(username)
        return user

    @classmethod
    def bulk_get_or_create(cls, usernames):
        users = list(User.objects.filter(username__in=usernames).all())
        existing_usernames = [user.username for user in users]

        missing_usernames = set(usernames) - set(existing_usernames)

        for username in missing_usernames:
            new_user = cls._create_non_registered(username)
            users.append(new_user)
        return users

    @classmethod
    def _create_non_registered(cls, username):
        user = User.objects.create_user(username, is_active=False)
        user.set_unusable_password()
        user.save()
        return user
