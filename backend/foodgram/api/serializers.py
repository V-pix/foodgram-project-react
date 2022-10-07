import base64
from djoser.serializers import UserSerializer
from requests import request
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from rest_framework import status

from django.shortcuts import get_object_or_404
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


class RecipeGetSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    # ingredients = RecipeIngredientsSerializer(
        # many=True, read_only=True, source="recipe_ingredients"
    # )
    ingredients = serializers.SerializerMethodField(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField(
        source="get_is_in_shopping_cart"
    )
    
    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )
        
    def get_ingredients(self, obj):
        queryset = RecipeIngredients.objects.filter(recipe=obj)
        return RecipeIngredientsSerializer(queryset, many=True).data
    
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


class RecipeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        required=True,
    )
    ingredients = RecipeIngredientsSerializer(
        many=True, # read_only=True, # source="recipe_ingredients"
    )
    # tags = TagSerializer(read_only=True, many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
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

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError("Выберите ингридиенты")
        return ingredients
    
    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError("Выберите теги")
        return tags
    
    def validate_cooking_time(self, cooking_time):
        if not cooking_time:
            raise serializers.ValidationError("Укажите время приготовления")
        return cooking_time
    
    def create(self, validated_data):
        context = self.context["request"]
        # print(context.data)
        author = self.context["request"].user
        # print(validated_data)
        # ingredients= context.data["ingredients"]
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data, author=author)
        # if recipe.exists():
            # raise serializers.ValidationError('Такой рецепт уже существует.')
        recipe.save()
        recipe.tags.set(tags)
        # for ingredient in ingredients:
            # print(ingredient)
        print(type(ingredients[0]['ingredient']['id']))
        # print(ingredients[1])
        # for ingredient in ingredients:
            # print(ingredient["id"])
        # for ingredient in ingredients:
            # print(type(ingredient["id"]))
        RecipeIngredients.objects.bulk_create([RecipeIngredients(
                ingredient=ingredients[0]['ingredient']['id'],
                recipe=recipe,
                amount=10,
            )])
        return recipe
        # RecipeIngredients.objects.bulk_create(RecipeIngredients(
                # ingredient=ingredients[0]['ingredient']['id'],
                # ingredient["id"],
                # ingredient_id=get_object_or_404(
                    # Ingredient,
                    # id=ingredient.get('id')
                # ),
                # recipe=recipe,
                # amount=ingredient["amount"],
            # )for ingredient in ingredients)
        # return recipe


    def update(self, instance, validated_data):
        tags = validated_data.get('tags')
        ingredients = validated_data.get('ingredients')
        print(validated_data)
        print(ingredients)
        if tags:
            instance.tags.clear()
            instance.tags.add(*tags)
        if ingredients:
            instance.ingredients.clear()
            for ingredient in ingredients:
                RecipeIngredients.objects.get_or_create(
                        recipe=instance,
                        # ingredients=ingredient['ingredient'][0],
                        ingredients=Ingredient.objects.get(id=ingredient["id"]),
                        amount=ingredient['amount']
                )
            #return instance
            return super().update(instance, validated_data)
    
    def update123(self, instance, validated_data):
        context = self.context["request"]
        tags = validated_data.pop('tags')
        ingredients = context.data["ingredients"]
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        for ingredient in ingredients:
            ingredient_model = Ingredient.objects.get(id=ingredient["id"])
            RecipeIngredients.objects.create(
                recipe=instance,
                ingredient=ingredient_model,
                amount=ingredient["amount"],
            )
        instance.save()
        return instance

    def update123(self, instance, validated_data):
        context = self.context["request"]
        tags_set = context.data["tags"]
        # instance.name = validated_data.get("name", instance.name)
        # instance.text = validated_data.get("text", instance.text)
        # instance.cooking_time = validated_data.get(
            # "cooking_time", instance.cooking_time
        # )
        # instance.image = validated_data.get("image", instance.image)
        # instance.save()
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
        return super().update(instance, validated_data)

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
        # validators = [
            # UniqueTogetherValidator(
                # queryset=Favorites.objects.all(),
                # fields=('user', 'recipe'),
                # message='Этот рецепт уже в избранном'
            # )
        # ]

    def create(self, validated_data):
        favorite = Favorites.objects.create(**validated_data)
        favorite.save()
        return favorite
    

class FavoritesValidSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())

    class Meta:
        model = Favorites
        fields = ('user', 'recipe')

    def validate(self, data):
        request = self.context.get('request')
        user = request.user
        recipe = self.context.get('recipe')
        favorite_recipe = Favorites.objects.filter(
            user_id=user,
            recipe_id=recipe
        )
        if request.method == 'POST':
            if favorite_recipe.exists():
                raise serializers.ValidationError({
                    'error': 'Рецепт уже добавлен в избранное.'
                })
        if request.method == 'DELETE':
            if not favorite_recipe.exists():
                raise serializers.ValidationError({
                    'error': 'Рецепта нет в избранном.'
                })
        return data


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
