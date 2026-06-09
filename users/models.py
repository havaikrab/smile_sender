from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Модель пользователя"""

    email = models.EmailField(unique=True, blank=False, null=False, verbose_name="Адрес электронной почты")
    first_name = models.CharField(blank=False, null=False, max_length=150, verbose_name="Имя")
    last_name = models.CharField(blank=False, null=False, max_length=150, verbose_name="Фамилия")
    phone: models.CharField = models.CharField(blank=True, null=True, max_length=15, verbose_name="Телефон")
    company: models.CharField = models.CharField(
        blank=True, null=True, max_length=150, verbose_name="Название организации"
    )
    customers: models.ManyToManyField = models.ManyToManyField(
        "distribution.Recipient",
        related_name="senders",
        verbose_name="Получатели",
        help_text="Список получателей",
        blank=True,
    )
    is_active = models.BooleanField(default=False)

    class Meta:
        """Настройки отображения"""

        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["email"]
        permissions = [
            ("block_customuser", "Может заблокировать аккаунт пользователя"),
            ("unblock_customuser", "Может разблокировать аккаунт пользователя"),
        ]

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "is_active"]

    def __str__(self) -> str:
        """Строковое представление пользователя"""

        return f"{self.username}: {self.email}"
