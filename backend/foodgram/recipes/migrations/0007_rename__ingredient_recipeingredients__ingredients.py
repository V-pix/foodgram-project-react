# Generated by Django 3.2.15 on 2022-09-20 14:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_recipeingredients__ingredient'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipeingredients',
            old_name='_ingredient',
            new_name='_ingredients',
        ),
    ]
