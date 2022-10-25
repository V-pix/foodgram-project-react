from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    USER = "user"
    ADMIN = "admin"

    USER_ROLES = (
        (USER, "Пользователь"),
        (ADMIN, "Администратор"),
    )

    role = models.CharField(
        verbose_name="Роль пользователя",
        max_length=50,
        default=USER,
        choices=USER_ROLES,
    )
    email = models.EmailField(
        max_length=254,
        verbose_name="Адрес электронной почты",
        help_text="Укажите Email",
        unique=True,
    )
    username = models.CharField(
        max_length=150,
        verbose_name="Логин пользователя",
        help_text="Укажите логин",
        unique=True,
    )
    first_name = models.TextField(
        max_length=150,
        verbose_name="Имя пользователя",
        help_text="Укажите имя",
    )
    last_name = models.TextField(
        max_length=150,
        verbose_name="Фамилия пользователя",
        help_text="Укажите фамилию",
    )
    password = models.CharField(
        max_length=150,
        verbose_name="Пароль пользователя",
        help_text="Придумайте пароль",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "username",
        "first_name",
        "last_name",
    ]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["username"]

        constraints = [
            models.UniqueConstraint(
                fields=["username", "email"], name="unique_user"
            )
        ]

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.is_superuser or self.role == "admin" or self.is_staff


class Subscribtion(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="subscriber",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="subscribing",
        verbose_name="Автор",
    )

    class Meta:
        ordering = ["-id"]
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
