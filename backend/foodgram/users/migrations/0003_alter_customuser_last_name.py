# Generated by Django 3.2.15 on 2022-09-18 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_customuser_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='last_name',
            field=models.TextField(help_text='Укажите фамилию', max_length=150, verbose_name='Фамилия пользователя'),
        ),
    ]
