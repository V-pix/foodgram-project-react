import base64

# from msilib.schema import Error


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
            "measure_unit",
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
        fields = ("id", "name", "measure_unit", "amount")


class RecipeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        required=True,
    )
    ingredients = RecipeIngredientsSerializer(many=True, source="recipe_ingredients")
    tags = TagSerializer(read_only=True, many=True)
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field="username",
        default=serializers.CurrentUserDefault(),
    )
    image = Base64ImageField(required=False, allow_null=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "author",
            "name",
            "image",
            "text",
            "ingredients",
            "tags",
            "cooking_time",
            "is_favorited",
            "is_in_shopping_cart",
        )
        read_only_fields = ("author",)

    def create(self, validated_data):
        context = self.context["request"]
        ingredients = validated_data.pop("recipe_ingredients")
        try:
            recipe = Recipe.objects.create(
                **validated_data, author=self.context.get("request").user
            )
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
        ingredients = validated_data.pop("recipe_ingredients")
        tags_set = context.data["tags"]
        # recipe = instance
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
        if request in None or request.user.is_anonymous:
            return False
        user = request.user
        return Favorites.objects.filter(recipe=data.id, user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get("request").user.id
        return ShoppingCart.objects.filter(user=user, recipe=obj.id).exists()

    # def get_is_in_shopping_cart(self, data):
    # request = self.context.get('request')
    # try:
    # user = self.context.get('request').user
    # except:
    # user = self.context.get('user')
    # queryset_shop = ShoppingCart.objects.filter(recipe=data, user=user)
    # return True


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

    def create(self, validated_data):
        favorite = Favorites.objects.create(**validated_data)
        favorite.save()
        return favorite

    class Meta:
        model = Favorites
        fields = ("id", "cooking_time", "name", "image")


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


# class TagSerializer(serializers.ModelSerializer):
# class Meta:
# model = Tag
# fields = '__all__'
