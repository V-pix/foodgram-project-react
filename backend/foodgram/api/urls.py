from django.urls import include, path
from rest_framework.routers import DefaultRouter
from django.contrib import admin

from api.views import CustomUserViewSet, IngredientViewSet, RecipeViewSet, TagViewSet

# app_name = "api"

router = DefaultRouter()
router.register(r"users", CustomUserViewSet, basename="users")
router.register("recipes", RecipeViewSet, basename="recipes")
router.register("tags", TagViewSet, basename="tags")
router.register("ingredients", IngredientViewSet, basename="ingredients")


urlpatterns = [
    path(
        
        "users/subscriptions/",
        CustomUserViewSet.as_view(
            {
                "get": "subscriptions",
            }
        ),
        name="subscriptions",
    ),
    path("auth/", include("djoser.urls.authtoken")),
    path("", include("djoser.urls")),
    path("", include(router.urls)),
]
