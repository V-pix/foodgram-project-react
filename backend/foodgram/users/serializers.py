from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from users.models import CustomUser, Subscribtion


class CustomUserSerializer(UserSerializer):
    def create(self, validated_data):
        user = CustomUser(
            email=validated_data["email"],
            username=validated_data["username"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user

    class Meta:
        model = CustomUser
        fields = ("email", "id", "username", "first_name", "last_name", "password")
        extra_kwargs = {"password": {"write_only": True}}

    # def set_password(self, instance, validated_data):
    # instance.set_password(validated_data['new_password'])
    # instance.save()
    # return instance


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("email", "username", "first_name", "last_name", "password")
        # extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser(
            email=validated_data["email"],
            username=validated_data["username"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class SubscribtionSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field="username",
        default=serializers.CurrentUserDefault(),
    )
    author = serializers.SlugRelatedField(
        slug_field="username", queryset=CustomUser.objects.all()
    )

    def validate_following(self, author):
        if self.context.get("request").user == author:
            raise serializers.ValidationError("Нельзя подписываться на самого себя")
        return author

    class Meta:
        model = Subscribtion
        fields = ("user", "author")

        validators = [
            UniqueTogetherValidator(
                queryset=Subscribtion.objects.all(), fields=("user", "author")
            )
        ]


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
        fields = ("username",)
