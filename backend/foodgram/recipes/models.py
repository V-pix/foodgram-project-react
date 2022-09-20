from colorfield.fields import ColorField
from django.db import models
from users.models import CustomUser


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название тега',
        help_text='Проверьте название тега',
        unique=True,
    )
    color = ColorField(
        default='#FF0000',
        unique=True,
    )
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


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
        verbose_name='Автор',
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта',
        help_text='Проверьте название рецепта',
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes/images/',
        blank=True
    )
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        # through='RecipeIngredients',
        related_name='recipe',
        blank=True,
        verbose_name='Ингредиенты блюда',
        help_text='Выберете ингридиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        # through='RecipeTags',
        related_name='recipe',
        verbose_name='Тэг блюда',
        help_text='Выберите тэг',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления блюда',
        help_text='Укажите время приготовления блюда',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredients(models.Model):
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиента',
        help_text='Укажите Количество ингредиента',
    )
    ingredients = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Ингредиенты блюда',
        help_text='Выберете ингридиенты',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт блюда',
        help_text='Опишите рецепт',
    )


class RecipeTags(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE,
                            related_name='recipe_tags')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='recipe_tags')


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


class ShoppingCart(models.Model):
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
