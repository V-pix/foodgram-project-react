import io

from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404

from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfbase import pdfmetrics, ttfonts
from reportlab.pdfgen import canvas

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import LimitPageNumberPagination
from api.serializers import (
    CustomUserSerializer,
    FavoritesSerializer,
    FavoritesValidSerializer,
    IngredientSerializer,
    RecipeGetSerializer,
    RecipeSerializer,
    RegistrationSerializer,
    ShoppingCartSerializer,
    ShoppingCartValidSerializer,
    SubscribtionsSerializer,
    SubscribtionValidSerializer,
    TagSerializer
)
from recipes.models import (
    Favorites,
    Ingredient,
    Recipe,
    RecipeIngredients,
    ShoppingCart,
    Tag
)
from users.models import CustomUser, Subscribtion


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == "GET":
            return RecipeGetSerializer
        return RecipeSerializer

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        url_path="favorite",
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk):
        user = request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        recipe = get_object_or_404(Recipe, pk=pk)
        data = {"user": request.user.id, "recipe": pk}
        serializer = FavoritesValidSerializer(
            data=data,
            context={"request": request, "recipe": recipe},
        )
        serializer.is_valid(raise_exception=True)
        if request.method == "POST":
            recipe = Favorites.objects.create(user=user, recipe=recipe)
            serializer = FavoritesSerializer(
                recipe, context={"request": request}
            )
            return Response(
                serializer.to_representation(instance=recipe),
                status=status.HTTP_201_CREATED,
            )
        Favorites.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        url_path="shopping_cart",
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):
        user = request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        recipe = get_object_or_404(Recipe, pk=pk)
        data = {"user": request.user.id, "recipe": pk}
        serializer = ShoppingCartValidSerializer(
            data=data,
            context={"request": request, "recipe": recipe},
        )
        serializer.is_valid(raise_exception=True)
        if request.method == "POST":
            recipe = ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = ShoppingCartSerializer(
                recipe, context={"request": request}
            )
            return Response(
                serializer.to_representation(instance=recipe),
                status=status.HTTP_201_CREATED,
            )
        ShoppingCart.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["get"],
        url_path="download_shopping_cart",
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        buf = io.BytesIO()
        page = canvas.Canvas(buf)
        arial = ttfonts.TTFont("Arial", "data/arial.ttf")
        pdfmetrics.registerFont(arial)

        x_position, y_position = 50, 800
        ingredients = (
            RecipeIngredients.objects.filter(
                recipe__shopping_cart__user=request.user
            )
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(total_amount=Sum("amount"))
            .order_by()
        )
        page.setFont("Arial", 14)
        if ingredients:
            indent = 20
            page.drawString(x_position, y_position, "Cписок покупок:")
            for index, ingredient in enumerate(ingredients, start=1):
                page.drawString(
                    x_position,
                    y_position - indent,
                    f'{index}. {ingredient["ingredient__name"]} - '
                    f'{ingredient["total_amount"]} '
                    f'{ingredient["ingredient__measurement_unit"]}.',
                )
                y_position -= 15
                if y_position <= 50:
                    page.showPage()
                    y_position = 800
            page.save()
            buf.seek(0)
            return FileResponse(
                buf, as_attachment=True, filename="shopping_cart.pdf"
            )
        page.setFont("Arial", 24)
        page.drawString(x_position, y_position, "Cписок покупок пуст!")
        page.save()
        buf.seek(0)
        return FileResponse(
            buf, as_attachment=True, filename="shopping_cart.pdf"
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientFilter,)
    search_fields = ("^name",)
    pagination_class = None


class UserRegistrationView(APIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegistrationSerializer
    permission_classes = (AllowAny,)
    pagination_class = None

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    filter_backends = (filters.SearchFilter,)
    filterset_fields = ("user", "author")
    search_fields = ("author__username",)

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk):
        user = request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        author = get_object_or_404(CustomUser, id=pk)
        data = {"user": user.id, "author": pk}
        serializer = SubscribtionValidSerializer(
            data=data,
            context={"request": request, "author": author},
        )
        serializer.is_valid(raise_exception=True)
        if request.method == "POST":
            author = Subscribtion.objects.create(user=user, author=author)
            return Response(
                serializer.to_representation(instance=author),
                status=status.HTTP_201_CREATED,
            )
        #  if request.method == "DELETE":
        Subscribtion.objects.filter(user=user, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        user = request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        queryset = CustomUser.objects.filter(subscribing__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribtionsSerializer(
            pages, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)
