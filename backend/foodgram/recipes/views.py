from cgitb import text
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
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

from recipes.models import Recipe, ShoppingCart, Tag, Ingredient, Favorites, RecipeIngredients
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
    #   permission_classes = (AllowAny,)

    @action(detail=True, methods=["POST", "DELETE"], url_path="favorite", permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk):
        current_user = self.request.user
        if current_user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        recipe = get_object_or_404(Recipe, pk=pk)
        recipe_in_favorite = Favorites.objects.filter(user=current_user, recipe=recipe)
        if request.method == "POST":
            # serializer = FavoritesSerializer(recipe)
            if recipe_in_favorite.exists():
                data = {"errors": "Этот рецепт уже есть в избранном."}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            recipe = Favorites.objects.create(user=current_user, recipe=recipe)
            serializer = FavoritesSerializer(recipe,
                context={'request': request})
            return Response(
                serializer.to_representation(instance=recipe),
                # serializer.data, 
                status=status.HTTP_201_CREATED
            )
            # return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE":
            if not recipe_in_favorite.exists():
                data = {"errors": "Этого рецепта нет в избранном пользователя."}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            recipe_in_favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["POST", "DELETE"], url_path="shopping_cart", permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk):
        current_user = request.user
        if current_user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        recipe = get_object_or_404(Recipe, pk=pk)
        recipe_in_shopping_cart = ShoppingCart.objects.filter(
            user=current_user, recipe=recipe
        )
        if request.method == "POST":
            # serializer = ShoppingCartSerializer(recipe)
            if recipe_in_shopping_cart.exists():
                data = {"errors": "Рецепт уже есть в списке покупок."}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            recipe = ShoppingCart.objects.create(user=current_user, recipe=recipe)
            serializer = ShoppingCartSerializer(recipe,
                context={'request': request})
            return Response(
                serializer.to_representation(instance=recipe),
                # serializer.data, 
                status=status.HTTP_201_CREATED
            )
        if request.method == "DELETE":
            if not recipe_in_shopping_cart.exists():
                data = {"errors": "Этого рецепта нет в списке покупок."}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            recipe_in_shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
    @action(
        detail=False,
        methods=['get'],
        url_path="download_shopping_cart",
        permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        buf = io.BytesIO()
        page = canvas.Canvas(buf, pagesize=letter, bottomup=0)
        pdfmetrics.registerFont(TTFont('DejaVuSans','DejaVuSans.ttf'))
        
        x_position, y_position = 50, 800
        shopping_cart = (
            request.user.shopping_cart.recipe.
            values(
                'ingredient__name',
                'ingredient__measurement_unit'
            ).annotate(amount=Sum('recipe__amount')).order_by())
        page.setFont('DejaVuSans', 14)
        if shopping_cart:
            indent = 20
            page.drawString(x_position, y_position, 'Cписок покупок:')
            for index, recipe in enumerate(shopping_cart, start=1):
                page.drawString(
                    x_position, y_position - indent,
                    f'{index}. {recipe["ingredient__name"]} - '
                    f'{recipe["amount"]} '
                    f'{recipe["ingredient__measurement_unit"]}.')
                y_position -= 15
                if y_position <= 50:
                    page.showPage()
                    y_position = 800
            page.save()
            buf.seek(0)
            return FileResponse(
                buf, as_attachment=True, filename="shopping_cart.pdf")
        page.setFont('DejaVuSans', 14)
        page.drawString(
            x_position,
            y_position,
            'Cписок покупок пуст!')
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
