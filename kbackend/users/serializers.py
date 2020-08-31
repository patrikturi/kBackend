from rest_framework import serializers

from users.models import User


class PasswordResetSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'uuid') # TODO: contain at most one . and uuid 36 length


class UserListItem(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'profile_picture_url', 'introduction')
