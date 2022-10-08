from cgitb import text
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.http import FileResponse, HttpResponse
import io
from django.db.models import F, Sum
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from users.models import CustomUser, Subscribtion
from recipes.models import (
    Recipe,
    ShoppingCart,
    Tag,
    Ingredient,
    Favorites,
    RecipeIngredients,
)
from api.serializers import (
    CustomUserSerializer,
    RegistrationSerializer,
    SubscribtionValidSerializer,
    SubscribtionsSerializer,
    FavoritesSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeGetSerializer,
    ShoppingCartSerializer,
    TagSerializer,
    FavoritesValidSerializer,
    ShoppingCartValidSerializer,
)
from api.filters import RecipeFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    # permission_classes = (OwnerOrAdminOrReadOnly,)
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
            serializer = FavoritesSerializer(recipe, context={"request": request})
            return Response(
                serializer.to_representation(instance=recipe),
                status=status.HTTP_201_CREATED,
            )
        if request.method == "DELETE":
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
            serializer = ShoppingCartSerializer(recipe, context={"request": request})
            return Response(
                serializer.to_representation(instance=recipe),
                status=status.HTTP_201_CREATED,
            )
        if request.method == "DELETE":
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
        page = canvas.Canvas(buf, pagesize=letter, bottomup=0)
        pdfmetrics.registerFont(TTFont("DejaVuSans", "DejaVuSans.ttf"))

        x_position, y_position = 50, 800
        shopping_cart = (
            request.user.shopping_cart.recipe.values(
                "ingredient__name", "ingredient__measurement_unit"
            )
            .annotate(amount=Sum("recipe__amount"))
            .order_by()
        )
        page.setFont("DejaVuSans", 14)
        if shopping_cart:
            indent = 20
            page.drawString(x_position, y_position, "Cписок покупок:")
            for index, recipe in enumerate(shopping_cart, start=1):
                page.drawString(
                    x_position,
                    y_position - indent,
                    f'{index}. {recipe["ingredient__name"]} - '
                    f'{recipe["amount"]} '
                    f'{recipe["ingredient__measurement_unit"]}.',
                )
                y_position -= 15
                if y_position <= 50:
                    page.showPage()
                    y_position = 800
            page.save()
            buf.seek(0)
            return FileResponse(buf, as_attachment=True, filename="shopping_cart.pdf")
        page.setFont("DejaVuSans", 14)
        page.drawString(x_position, y_position, "Cписок покупок пуст!")
        page.save()
        buf.seek(0)
        return FileResponse(buf, as_attachment=True, filename="shopping_cart.pdf")


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


class UserRegistrationView(APIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegistrationSerializer
    permission_classes = (AllowAny,)
    pagination_class = None

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            username = request.data.get("username")
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    filter_backends = (filters.SearchFilter,)
    filterset_fields = ("user", "author")
    search_fields = ("author__username",)

    @action(
        detail=True, methods=["POST", "DELETE"], permission_classes=[IsAuthenticated]
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
        serializer.save()
        if request.method == "POST":
            author = Subscribtion.objects.create(user=user, author=author)
            # serializer = SubscribtionsSerializer(author, context={"request": request})
            return Response(
                serializer.to_representation(instance=author),
                status=status.HTTP_201_CREATED,
            )
        if request.method == "DELETE":
            Subscribtion.objects.filter(user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    def subscribe13(self, request, pk):
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
        # serializer.save()
        if request.method == "POST":
            follow = Subscribtion.objects.create(user=user, author=author)
            serializer = SubscribtionsSerializer(follow, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        follow = Subscribtion.objects.filter(user=user, author=author)
        if request.method == "DELETE":
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        current_user = request.user
        if current_user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        queryset = CustomUser.objects.filter(subscribing__user=current_user)
        paginator = PageNumberPagination()
        paginator.page_size_query_param = "limit"
        pages = self.paginate_queryset(queryset)
        serializer = SubscribtionsSerializer(
            pages, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)
