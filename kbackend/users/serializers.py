from rest_framework import serializers

from users.models import User, UserDetails


class PasswordResetSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'uuid') # TODO: contain at most one . and uuid 36 length


class UserListItem(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'profile_picture_url', 'introduction')


class UserDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserDetails
        fields = ('id', 'biography', 'updated_at')


class UserProfileSerializer(serializers.ModelSerializer):
    user_details = UserDetailsSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'profile_picture_url', 'introduction',
        'ksoccer_points', 'goals', 'assists', 'matches', 'available_for_transfer',
        'date_joined')
