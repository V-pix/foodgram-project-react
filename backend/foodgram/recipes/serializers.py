import base64
from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from django.db import IntegrityError
from django.core.files.base import ContentFile
from django.forms import models
from rest_framework import serializers

from recipes.models import (
    Favorites,
    Ingredient,
    Recipe,
    RecipeIngredients,
    ShoppingCart,
    Tag,
    RecipeTags,
)

from users.models import CustomUser, Subscribtion


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


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            "id",
            "name",
            "measurement_unit",
        )


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]

            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)

        return super().to_internal_value(data)


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source="ingredient.id"
    )
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(source="ingredient.measurement_unit")

    class Meta:
        model = RecipeIngredients
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        required=True,
    )
    ingredients = RecipeIngredientsSerializer(
        many=True, read_only=True, source="recipe_ingredients"
    )
    tags = TagSerializer(read_only=True, many=True)
    author = CustomUserSerializer(
        read_only=True, default=serializers.CurrentUserDefault()
    )
    image = Base64ImageField(required=False, allow_null=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField(
        source="get_is_in_shopping_cart"
    )

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        read_only_fields = ("author",)

    def create(self, validated_data):
        context = self.context["request"]
        author = self.context["request"].user
        try:
            recipe = Recipe.objects.create(**validated_data, author=author)
        except IntegrityError as err:
            pass
        tags_set = context.data["tags"]
        for tag in tags_set:
            RecipeTags.objects.create(recipe=recipe, tag=Tag.objects.get(id=tag))
        ingredients_set = context.data["ingredients"]
        for ingredient in ingredients_set:
            ingredient_model = Ingredient.objects.get(id=ingredient["id"])
            RecipeIngredients.objects.create(
                recipe=recipe,
                ingredient=ingredient_model,
                amount=ingredient["amount"],
            )
        return recipe

    def update(self, instance, validated_data):
        context = self.context["request"]
        tags_set = context.data["tags"]
        instance.name = validated_data.get("name", instance.name)
        instance.text = validated_data.get("text", instance.text)
        instance.cooking_time = validated_data.get(
            "cooking_time", instance.cooking_time
        )
        instance.image = validated_data.get("image", instance.image)
        instance.save()
        instance.tags.set(tags_set)
        RecipeIngredients.objects.filter(recipe=instance).delete()
        ingredients_request = context.data["ingredients"]
        for ingredient in ingredients_request:
            ingredient_model = Ingredient.objects.get(id=ingredient["id"])
            RecipeIngredients.objects.create(
                recipe=instance,
                ingredient=ingredient_model,
                amount=ingredient["amount"],
            )
        return instance

    def get_is_favorited(self, data):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        user = request.user
        return Favorites.objects.filter(recipe=data.id, user=user).exists()

    def get_is_in_shopping_cart(self, data):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        user = request.user
        return ShoppingCart.objects.filter(recipe=data, user=user).exists()


class FavoritesSerializer(serializers.ModelSerializer):
    id = serializers.CharField(
        read_only=True,
        source="recipe.id",
    )
    cooking_time = serializers.CharField(
        read_only=True,
        source="recipe.cooking_time",
    )
    image = serializers.CharField(
        read_only=True,
        source="recipe.image",
    )
    name = serializers.CharField(
        read_only=True,
        source="recipe.name",
    )

    class Meta:
        model = Favorites
        fields = ("id", "cooking_time", "name", "image")

    def create(self, validated_data):
        favorite = Favorites.objects.create(**validated_data)
        favorite.save()
        return favorite


class ShoppingCartSerializer(serializers.ModelSerializer):
    id = serializers.CharField(
        read_only=True,
        source="recipe.id",
    )
    cooking_time = serializers.CharField(
        read_only=True,
        source="recipe.cooking_time",
    )
    image = serializers.CharField(
        read_only=True,
        source="recipe.image",
    )
    name = serializers.CharField(
        read_only=True,
        source="recipe.name",
    )

    class Meta:
        model = ShoppingCart
        fields = ("id", "cooking_time", "name", "image")


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

    def to_representation(self, instance):
        return SubscriptionsSerializer(
            instance.author, context={"request": self.context.get("request")}
        ).data


class SubscriptionsSerializer(serializers.ModelSerializer):

    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Subscribtion.objects.all(), fields=("user", "author")
            )
        ]

    def get_recipes(self, obj):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        recipes_limit = request.query_params.get("recipes_limit")
        queryset = Recipe.objects.filter(author=obj)
        if recipes_limit:
            queryset = queryset[: int(recipes_limit)]
        return RecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    def get_is_subscribed(self, data):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return Subscribtion.objects.filter(
            author=data, user=self.context.get("request").user
        ).exists()

    def validate_following(self, data):
        author = self.instance
        user = self.context.get("request").user
        if user == author:
            raise serializers.ValidationError("Нельзя подписываться на самого себя")
        return data
