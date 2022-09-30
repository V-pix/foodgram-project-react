# Generated by Django 3.2.15 on 2022-09-18 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="email",
            field=models.EmailField(
                help_text="Укажите Email",
                max_length=254,
                unique=True,
                verbose_name="Адрес электронной почты",
            ),
        ),
    ]
