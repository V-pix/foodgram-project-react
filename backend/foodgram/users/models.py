from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    USER = 'user'
    ADMIN = 'admin'

    USER_ROLES = (
        (USER, 'Пользователь'),
        (ADMIN, 'Администратор'),
    )

    role = models.CharField(
        verbose_name='Роль пользователя',
        max_length=50,
        default=USER,
        choices=USER_ROLES,
    )
    email = models.EmailField(
        max_length=254,
        verbose_name='Почта',
        help_text='Укажите Email',
        unique=True,
    )
    username = models.CharField(
        max_length=150,
        verbose_name='Логин пользователя',
        help_text='Укажите логин',
        unique=True,
    )
    first_name = models.TextField(
        max_length=150,
        verbose_name='Имя пользователя',
        help_text='Укажите имя',
    )
    last_name = models.TextField(
        max_length=150,
        verbose_name='Имя пользователя',
        help_text='Укажите фамилию',
    )
    password = models.CharField(
        max_length=150,
        verbose_name='Пароль пользователя',
        help_text='Придумайте пароль',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'], name='unique_user')
        ]

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.is_superuser or self.role == "admin" or self.is_staff


class Subscribtion()
