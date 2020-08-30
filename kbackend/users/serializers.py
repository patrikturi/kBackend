from rest_framework import serializers

from users.models import User


class PasswordResetSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'uuid') # TODO: contain at most one . and uuid 36 length
