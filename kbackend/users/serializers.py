from rest_framework import serializers

from users.models import User, UserDetails


class PasswordResetSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'display_name', 'email', 'uuid', 'password')


class UserListItem(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'display_name', 'profile_picture_url', 'introduction')


class UserDetailsSerializer(serializers.ModelSerializer):
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = UserDetails
        fields = ('id', 'biography', 'updated_at')


class UserDetailsCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserDetails
        fields = ('id', 'user', 'biography')


class UserDetailsEditSerializer(UserDetailsCreateSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)


class LoginSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'display_name', 'profile_picture_url')


class UserProfileSerializer(serializers.ModelSerializer):
    user_details = UserDetailsSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'display_name', 'profile_picture_url', 'introduction', 'user_details',
                  'kcoins', 'goals', 'assists', 'matches', 'available_for_transfer', 'date_joined')


class UserProfileEditSerializer(serializers.ModelSerializer):
    user_details = UserDetailsEditSerializer()

    nested_serializer = None

    class Meta:
        model = User
        fields = ('id', 'introduction', 'available_for_transfer', 'user_details')

    def update(self, instance, validated_data):
        own_data = {key: value for key, value in validated_data.items() if key != 'user_details'}
        super().update(instance, own_data)

        if 'user_details' in validated_data:
            self._update_user_details(instance.id, validated_data['user_details'])

        return instance

    def _update_user_details(self, user_id, data):
        instance = UserDetails.objects.filter(user_id=user_id).first()
        data['user'] = user_id
        if instance is None:
            serializer = UserDetailsCreateSerializer(data=data)
        else:
            serializer = UserDetailsEditSerializer(instance, data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        self.nested_serializer = serializer

    def to_representation(self, data):
        data = super().to_representation(data)

        if self.nested_serializer:
            data['user_details'] = self.nested_serializer.data
        return data


class PrivateUserProfileSerializer(UserProfileSerializer):
    pass
