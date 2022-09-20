# Generated by Django 3.2.15 on 2022-09-20 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_auto_20220920_1439'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(help_text='Выберите тэг', related_name='recipe', through='recipes.RecipeTags', to='recipes.Tag', verbose_name='Тэги блюда'),
        ),
    ]
