from django.contrib import admin

from recipes.models import (
    Favorites,
    Ingredient,
    Recipe,
    RecipeIngredients,
    RecipeTags,
    ShoppingCart,
    Tag
)


class IngredientInline(admin.TabularInline):
    model = RecipeIngredients
    extra = 1


class TagInline(admin.TabularInline):
    model = RecipeTags
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "author",
    )
    list_filter = (
        "author",
        "name",
        "tags",
    )
    readonly_fields = ("count_favourites",)
    search_fields = ("name", "author", "tags")
    empty_value_display = "-пусто-"
    inlines = [TagInline, IngredientInline]

    def favorited(self, obj):
        return Favorites.objects.filter(recipe=obj).count()

    favorited.short_description = "В избранном"


class TagAdmin(admin.ModelAdmin):
    inlines = [TagInline]
    list_display = ("name", "color")
    list_filter = ("name",)
    search_fields = ("name",)


class IngredientAdmin(admin.ModelAdmin):
    inlines = [IngredientInline]
    list_display = ("name", "measurement_unit")
    list_filter = ("name",)
    search_fields = ("name",)


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(ShoppingCart)
admin.site.register(Favorites)
