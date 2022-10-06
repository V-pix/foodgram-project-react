from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from django.contrib.auth import get_user_model
from users.models import CustomUser, Subscribtion

# from recipes.models import Recipe
# from recipes.serializers import RecipeSerializer

# User = get_user_model()


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

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

    def get_is_subscribed(self, data):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        user = request.user
        return Subscribtion.objects.filter(user=user, author=data).exists()

    class Meta:
        model = CustomUser
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
            "is_subscribed",
        )
        extra_kwargs = {"password": {"write_only": True}}

    # def set_password(self, instance, validated_data):
    # instance.set_password(validated_data['new_password'])
    # instance.save()
    # return instance


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("email", "id", "username", "first_name", "last_name", "password")
        extra_kwargs = {"password": {"write_only": True}}

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
    # username = serializers.CharField(
    # required=True
    # )
    # id = serializers.ReadOnlyField(source='author.id')

    class Meta:
        model = Subscribtion
        fields = ("user", "author")
        validators = [
            UniqueTogetherValidator(
                queryset=Subscribtion.objects.all(),
                fields=("user", "author"),
                message="Вы уже подписаны на этого автора",
            )
        ]

    def validate_following(self, data):
        author = self.instance
        user = self.context.get("request").user
        if user == author:
            raise serializers.ValidationError("Нельзя подписываться на самого себя")
        return data


class SubscriptionsSerializer(serializers.ModelSerializer):

    is_subscribed = serializers.SerializerMethodField(read_only=True)
    # recipes = serializers.SerializerMethodField(read_only=True)
    # recipes_count = serializers.IntegerField(source='recipes.count', read_only=True)

    class Meta:
        model = CustomUser
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",  # 'recipes', 'recipes_count'
        )

    # def get_recipes(self, obj):
    # request = self.context.get('request')
    # if request is None or request.user.is_anonymous:
    # return False
    # recipes_limit = request.query_params.get('recipes_limit')
    # queryset = Recipe.objects.filter(author=obj)
    # if recipes_limit:
    # queryset = queryset[:int(recipes_limit)]
    # return RecipeSerializer(queryset, many=True).data

    def get_is_subscribed(self, data):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return Subscribtion.objects.filter(
            author=data, user=self.context.get("request").user
        ).exists()


class SubscribtionSerializer123(serializers.ModelSerializer):
    # username = serializers.SlugRelatedField(
    # read_only=True,
    # required=True,
    # slug_field="username",
    # queryset=CustomUser.objects.all(),
    # default=serializers.CurrentUserDefault(),)
    is_subscribed = serializers.SerializerMethodField()
    id = serializers.ReadOnlyField(source="author.id")
    email = serializers.ReadOnlyField(source="author.email")
    username = serializers.ReadOnlyField(source="author.username")
    first_name = serializers.ReadOnlyField(source="author.first_name")
    last_name = serializers.ReadOnlyField(source="author.last_name")

    class Meta:
        model = CustomUser
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            # 'recipes', 'recipes_count',
            "is_subscribed",
        )
        read_only_fields = ("email", "username", "first_name", "last_name")
        # validators = [
        # UniqueTogetherValidator(
        # queryset=Subscribtion.objects.all(), fields=("user", "author")
        # )
        # ]

    def create(self, validated_data):
        subscribe = Subscribtion.objects.create(**validated_data)
        subscribe.save()
        return subscribe

    def validate_following(self, data):
        author = self.instance
        user = self.context.get("request").user
        if user == author:
            raise serializers.ValidationError("Нельзя подписываться на самого себя")
        return data

    def get_is_subscribed(self, data):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return Subscribtion.objects.filter(
            author=data, user=self.context.get("request").user
        ).exists()
