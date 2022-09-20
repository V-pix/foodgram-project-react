import base64

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
)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measure_unit',)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measure_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True)
    tags = TagSerializer(many=True)
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault(),
    )
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = ('author', 'name', 'image', 'text', 'ingredients',
                  'tags', 'cooking_time', 'pub_date')
        read_only_fields = ('author',)

    def create(self, validated_data):
        if 'ingredients' not in self.initial_data:
            cat = Recipe.objects.create(**validated_data)
            return cat
        else:
            ingredients = validated_data.pop('ingredients')
            recipe = Recipe.objects.create(**validated_data)
            for ingredient in ingredients:
                current_ingredient, status = Ingredient.objects.get_or_create(
                    **ingredient
                )
                RecipeIngredients.objects.create(
                    achievement=current_ingredient, recipe=recipe
                )
            return recipe

    # def update(self, instance, validated_data):
        # instance.name = validated_data.get('name', instance.name)
        # instance.color = validated_data.get('color', instance.color)
        # instance.birth_year = validated_data.get(
            # 'birth_year', instance.birth_year
        # )
        # instance.image = validated_data.get('image', instance.image)
        # if 'achievements' in validated_data:
            # achievements_data = validated_data.pop('achievements')
            # lst = []
            # for achievement in achievements_data:
            # current_achievement, status = Achievement.objects.get_or_create(
            # **achievement
            # )
            # lst.append(current_achievement)
            # instance.achievements.set(lst)

        instance.save()
        return instance

    # def get_is_favorited(self, obj):

    # def get_is_in_shopping_cart(self, obj):


class FavoritesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorites
        fields = '__all__'


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = '__all__'

# class TagSerializer(serializers.ModelSerializer):
    # class Meta:
        # model = Tag
        # fields = '__all__'
