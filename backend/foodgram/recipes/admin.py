from django.contrib import admin

from recipes.models import (
    Favorites,
    Ingredient,
    Recipe,
    RecipeIngredients,
    ShoppingCart,
    Tag,
)

admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Recipe)
