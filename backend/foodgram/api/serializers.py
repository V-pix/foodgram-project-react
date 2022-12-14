import base64

from django.core.files.base import ContentFile

from rest_framework import serializers

from djoser.serializers import UserSerializer

from recipes.models import (
    Favorites,
    Ingredient,
    Recipe,
    RecipeIngredients,
    ShoppingCart,
    Tag
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


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            "email", "id", "username", "first_name", "last_name", "password"
        )
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


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]

            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)

        return super().to_internal_value(data)


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


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source="ingredient.id"
    )
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = RecipeIngredients
        fields = ("id", "amount", "name", "measurement_unit")


class RecipeGetSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
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
    author = CustomUserSerializer(
        read_only=True, default=serializers.CurrentUserDefault()
    )
    ingredients = RecipeIngredientsSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        read_only_fields = ("author",)

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError("???????????????? ????????")
        return tags

    def validate_cooking_time(self, cooking_time):
        if not cooking_time:
            raise serializers.ValidationError("?????????????? ?????????? ??????????????????????????")
        return cooking_time

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError("???????????????? ??????????????????????")
        ingredients_recipe = self.initial_data.get("ingredients")
        ingredients_list = []
        for ingredient in ingredients_recipe:
            if ingredient["id"] in ingredients_list:
                raise serializers.ValidationError(
                    {"ingredients": "?????????????????????? ???? ???????????? ??????????????????????"}
                )
            ingredients_list.append(ingredient["id"])
        return ingredients_recipe

    def ingredient_create(self, recipe, ingredients):
        RecipeIngredients.objects.bulk_create(
            [
                RecipeIngredients(
                    ingredient_id=ingredient_item["id"],
                    recipe_id=recipe.id,
                    amount=ingredient_item.get("amount"),
                )
                for ingredient_item in ingredients
            ]
        )

    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(
            author=self.context.get("request").user, **validated_data
        )
        recipe.save()
        recipe.tags.set(tags)
        self.ingredient_create(recipe, ingredients)
        return recipe

    def update(self, recipe, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe.tags.clear()
        recipe.ingredients.clear()
        recipe.tags.set(tags)
        self.ingredient_create(recipe, ingredients)
        recipe.save()
        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        request = self.context.get("request")
        context = {"request": request}
        return RecipeGetSerializer(instance, context=context).data


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


class FavoritesValidSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all()
    )

    class Meta:
        model = Favorites
        fields = ("user", "recipe")

    def validate(self, data):
        request = self.context.get("request")
        user = request.user
        recipe = self.context.get("recipe")
        favorite_recipe = Favorites.objects.filter(
            user_id=user, recipe_id=recipe
        )
        if request.method == "POST":
            if favorite_recipe.exists():
                raise serializers.ValidationError(
                    "???????????? ?????? ???????????????? ?? ??????????????????."
                )
        if request.method == "DELETE":
            if not favorite_recipe.exists():
                raise serializers.ValidationError("?????????????? ?????? ?? ??????????????????.")
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


class ShoppingCartValidSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ("user", "recipe")

    def validate(self, data):
        request = self.context.get("request")
        user = request.user
        recipe = data["recipe"]
        shopping_cart_recipe = ShoppingCart.objects.filter(
            user=user, recipe=recipe
        )
        if request.method == "POST":
            if shopping_cart_recipe.exists():
                raise serializers.ValidationError(
                    "???????????? ?????? ???????? ?? ???????????? ??????????????."
                )
        if request.method == "DELETE":
            if not shopping_cart_recipe.exists():
                raise serializers.ValidationError(
                    "?????????? ?????????????? ?????? ?? ???????????? ??????????????."
                )
        return data


class SubscribtionsSerializer(serializers.ModelSerializer):
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

    def get_recipes(self, obj):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        recipes_limit = request.query_params.get("recipes_limit")
        queryset = Recipe.objects.filter(author=obj)
        if recipes_limit:
            queryset = queryset[: int(recipes_limit)]
        return SubscribtionRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    def get_is_subscribed(self, author):
        return Subscribtion.objects.filter(
            user=self.context.get("request").user, author=author
        ).exists()


class SubscribtionRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class SubscribtionValidSerializer(serializers.ModelSerializer):
    queryset = CustomUser.objects.all()
    user = serializers.PrimaryKeyRelatedField(queryset=queryset)
    author = serializers.PrimaryKeyRelatedField(queryset=queryset)

    class Meta:
        model = Subscribtion
        fields = ("user", "author")

    def validate(self, data):
        request = self.context.get("request")
        author = data["author"].id
        user = self.context.get("request").user
        follow = Subscribtion.objects.filter(user=user, author=author)
        if request.method == "POST":
            if user == author:
                raise serializers.ValidationError(
                    "???????????? ?????????????????????????? ???? ???????????? ????????."
                )
            if follow.exists():
                raise serializers.ValidationError(
                    "???? ?????? ?????????????????? ???? ?????????? ????????????????????????"
                )
        if request.method == "DELETE":
            if not follow.exists():
                raise serializers.ValidationError(
                    "???? ???? ?????????????????? ???? ?????????? ????????????."
                )
        return data

    def to_representation(self, instance):
        return SubscribtionsSerializer(
            instance.author, context={"request": self.context.get("request")}
        ).data
