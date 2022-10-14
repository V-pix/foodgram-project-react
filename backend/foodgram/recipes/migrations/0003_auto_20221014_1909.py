# Generated by Django 3.2.15 on 2022-10-14 19:09

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_rename_measure_unit_ingredient_measurement_unit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(help_text='Укажите время приготовления блюда в минутах', validators=[django.core.validators.MinValueValidator(1, 'Время приготовления не может быть меньше 1 минуты')], verbose_name='Время приготовления блюда'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(blank=True, upload_to='', verbose_name='Картинка'),
        ),
        migrations.AlterField(
            model_name='recipeingredients',
            name='amount',
            field=models.PositiveSmallIntegerField(help_text='Укажите Количество ингредиента', validators=[django.core.validators.MinValueValidator(1, 'Количество ингридаента не может быть меньше 1 штуки')], verbose_name='Количество ингредиента'),
        ),
    ]
