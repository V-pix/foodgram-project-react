from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

from recipes.models import Recipe, ShoppingCart, Tag, Ingredient, Favorites
from recipes.serializers import (
    FavoritesSerializer,
    IngredientSerializer,
    RecipeSerializer,
    ShoppingCartSerializer,
    TagSerializer,
)
from recipes.filters import RecipeFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["POST", "DELETE"], url_path="favorite")
    def favorite(self, request, pk):
        current_user = self.request.user
        if current_user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        recipe = get_object_or_404(Recipe, pk=pk)
        recipe_in_favorite = Favorites.objects.filter(user=current_user, recipe=recipe)
        if request.method == "POST":
            serializer = FavoritesSerializer(recipe)
            if recipe_in_favorite.exists():
                data = {"errors": "Этот рецепт уже есть в избранном."}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            Favorites.objects.create(user=current_user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE":
            if not recipe_in_favorite.exists():
                data = {"errors": "Этого рецепта нет в избранном пользователя."}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            recipe_in_favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["POST", "DELETE"], url_path="shopping_cart")
    def shopping_cart(self, request, pk):
        current_user = self.request.user
        if current_user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        recipe = get_object_or_404(Recipe, pk=pk)
        recipe_in_shopping_cart = ShoppingCart.objects.filter(
            user=current_user, recipe=recipe
        )
        if request.method == "POST":
            serializer = ShoppingCartSerializer(recipe)
            if recipe_in_shopping_cart.exists():
                data = {"errors": "Рецепт уже есть в списке покупок."}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            ShoppingCart.objects.create(user=current_user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE":
            if not recipe_in_shopping_cart.exists():
                data = {"errors": "Этого рецепта нет в списке покупок."}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            recipe_in_shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    search_fields = ("^name",)
    pagination_class = None
