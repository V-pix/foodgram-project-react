from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from recipes.models import (
    Favorites,
    Ingredient,
    Recipe,
    RecipeIngredients,
    ShoppingCart,
    Tag,
)
from recipes.serializers import (
    FavoritesSerializer,
    IngredientSerializer,
    RecipeIngredientsSerializer,
    RecipeSerializer,
    ShoppingCartSerializer,
    TagSerializer,
)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AllowAny,)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter)
    search_fields = ('name',)


# @api_view(['GET'])
# def tags_list(request):
    # tags = Tag.objects.all()
    # serializer = TagSerializer(tags, many=True)
    # return Response(serializer.data)

# Если бы пользователи могли оставлять комментарии к котикам,
# то эндпоинт для работы с комментариями выглядел бы примерно так:
# cats/{cat_id}/comments/

# class CommentViewSet(viewsets.ModelViewSet):
    # serializer_class = CommentSerializer
    # queryset во вьюсете не указываем
    # Нам тут нужны не все комментарии, а только связанные с котом с id=cat_id
    # Поэтому нужно переопределить метод get_queryset и применить фильтр
    # def get_queryset(self):
    # Получаем id котика из эндпоинта
    # cat_id = self.kwargs.get("cat_id")
    # И отбираем только нужные комментарии
    # new_queryset = Comment.objects.filter(cat=cat_id)
    # return new_queryset
