from colorfield.fields import ColorField
from django.db import models
from users.models import CustomUser


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название тега',
        help_text='Проверьте название тега',
    )
    color = ColorField(default='#FF0000')
    slug = models.SlugField(unique=True)


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название ингредиента',
        help_text='Проверьте название ингредиента',
    )
    measure_unit = models.CharField(
        max_length=200,
        verbose_name='Единицы измерения',
        help_text='Проверьте единицы измерения',
    )


class Recipe(models.Model):
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name="Автор",
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта',
        help_text='Проверьте название рецепта',
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes/',
        blank=True
    )
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipe',
        blank=True,
        verbose_name='Ингредиенты блюда',
        help_text='Выберете ингридиенты',
    )
    tags = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления блюда',
        help_text='Укажите время приготовления блюда',
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.text


class RecipeIngredients(models.Model):
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиента',
        help_text='Укажите Количество ингредиента',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipe_ingredients',
        blank=True,
        verbose_name='Ингредиенты блюда',
        help_text='Выберете ингридиенты',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )


class Favorites(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
    )


class Shopping_cart(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )
