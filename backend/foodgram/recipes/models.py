from colorfield.fields import ColorField
from django.db import models
from users.models import User


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название тега',
        help_text='Проверьте название тега',
    )
    color = ColorField(default='#FF0000')
    slug = models.SlugField(unique=True)


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
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
        # RecipeIngredients,
        related_name='recipe',
        blank=True,
        verbose_name='Ингредиенты блюда',
        help_text='Выберете ингридиенты',
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE
    )
    time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления блюда',
        help_text='Укажите время приготовления блюда',
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.text
