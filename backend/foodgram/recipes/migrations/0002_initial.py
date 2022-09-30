# Generated by Django 3.2.15 on 2022-09-12 19:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("recipes", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="shoppingcart",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="shopping_cart",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="recipeingredients",
            name="ingredients",
            field=models.ManyToManyField(
                blank=True,
                help_text="Выберете ингридиенты",
                related_name="recipe_ingredients",
                to="recipes.Ingredient",
                verbose_name="Ингредиенты блюда",
            ),
        ),
        migrations.AddField(
            model_name="recipeingredients",
            name="recipe",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="recipe_ingredients",
                to="recipes.recipe",
            ),
        ),
        migrations.AddField(
            model_name="recipe",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="recipe",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Автор",
            ),
        ),
        migrations.AddField(
            model_name="recipe",
            name="ingredients",
            field=models.ManyToManyField(
                blank=True,
                help_text="Выберете ингридиенты",
                related_name="recipe",
                to="recipes.Ingredient",
                verbose_name="Ингредиенты блюда",
            ),
        ),
        migrations.AddField(
            model_name="recipe",
            name="tags",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="recipes.tag"
            ),
        ),
        migrations.AddField(
            model_name="favorites",
            name="recipe",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="favorites",
                to="recipes.recipe",
            ),
        ),
        migrations.AddField(
            model_name="favorites",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="favorites",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Пользователь",
            ),
        ),
    ]
