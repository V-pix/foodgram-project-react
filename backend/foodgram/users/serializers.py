from djoser.serializers import UserSerializer
from rest_framework import serializers

from users.models import CustomUser


class CustomUserSerializer(UserSerializer):
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name',
                  'last_name', 'password', 'role')


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('email', 'username')


class ObtainTokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=50)
    # confirmation_code = serializers.CharField(max_length=15)

    class Meta:
        model = CustomUser
        # fields = ('username', 'confirmation_code')
        fields = ('username', )
