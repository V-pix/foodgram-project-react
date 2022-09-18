from djoser.serializers import UserSerializer
from rest_framework import serializers

from users.models import CustomUser


class CustomUserSerializer(UserSerializer):
    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    # def set_password(self, instance, validated_data):
        # instance.set_password(validated_data['new_password'])
        # instance.save()
        # return instance


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name',
                  'last_name', 'password')
        # extra_kwargs = {'password': {'write_only': True}}


# class SetPasswordSerializer(serializers.ModelSerializer):
    # class Meta:
        # model = CustomUser
        # fields = ('new_password', 'current_password')

    # def set_password(self, instance, validated_data):
        # instance.set_password(validated_data['new_password'])
        # instance.save()
        # return instance


class ObtainTokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=50)
    # confirmation_code = serializers.CharField(max_length=15)

    class Meta:
        model = CustomUser
        # fields = ('username', 'confirmation_code')
        fields = ('username', )
