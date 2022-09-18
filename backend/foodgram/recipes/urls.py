from django.urls import include, path
from rest_framework.routers import DefaultRouter

from recipes.views import IngredientViewSet, RecipeViewSet, TagViewSet

app_name = 'recipes'

router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
]

# urlpatterns = [
# path('recipes/', recipes_list, name='recipes_list'),
# path('ingredients/', ingredients_list, name='ingredients_list'),
# path('tags/', tags_list, name='tags_list'),
# path('tags/', TagList.as_view()),
# path('tags/<int:pk>/', TagDetail.as_view()),
# path('users/set_password/'),]
