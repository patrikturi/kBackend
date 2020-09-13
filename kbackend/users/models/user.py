from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


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

    # http://wiki.secondlife.com/wiki/UUID
    uuid_validator = RegexValidator(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$')

    uuid = models.CharField(max_length=36, help_text='SL uuid: string of 32 hex characters with four dashes interspersed',
                            validators=[uuid_validator], blank=True)

    is_test = models.BooleanField(default=False)

    introduction = models.CharField(max_length=255, blank=True)

    available_for_transfer = models.BooleanField(default=False)

    ksoccer_points = models.IntegerField(default=0)
    goals = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    matches = models.IntegerField(default=0)

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

    @classmethod
    def reset_password(cls, username, uuid, password):
        from users.serializers import PasswordResetSerializer

        user = User.objects.filter(username=username).first()

        is_new = user is None
        if user:
            if user.uuid and user.uuid != uuid:
                return None, False
            user.is_active = True
            user.uuid = uuid
            user.set_password(password)
            user.save()
        else:
            serializer = PasswordResetSerializer(data={'username': username, 'uuid': uuid})
            if not serializer.is_valid():
                return None, False
            user = User.objects.create_user(username, email='', uuid=uuid, password=password)
        return user, is_new

    @classmethod
    def get_or_create(cls, username):
        user = User.objects.filter(username=username).first()

        if not user:
            # Create non-registered user
            user = User.objects.create_user(username, is_active=False)
            user.set_unusable_password()
            user.save()
        return user
