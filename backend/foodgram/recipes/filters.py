# from crypt import methods
from dataclasses import fields
from django_filters.rest_framework import filters, FilterSet
import django_filters

from recipes.models import Tag, Recipe


class RecipeFilter(django_filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name="tags_slug",
        queryset=Tag.objects.all(),
        to_field_name="slug",
    )
    is_favorited = filters.BooleanFilter(method="get_is_favorited")
    is_in_shopping_cart = filters.BooleanFilter(method="get_is_in_shopping_cart")

    class Meta:
        model = Recipe
        fields = ("tags",)

    def get_is_favorited(self, queryset, name, value):
        if value and not self.request.user.is_anonimous:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value and not self.request.user.is_anonimous:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset
