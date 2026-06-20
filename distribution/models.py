from django.db import models

from users.models import CustomUser


class Recipient(models.Model):
    """Модель получателя рассылки"""

    email: models.EmailField = models.EmailField(unique=True, verbose_name="Электронная почта получателя")
    first_name: models.CharField = models.CharField(
        max_length=50, verbose_name="Имя получателя", blank=True, null=True
    )
    middle_name: models.CharField = models.CharField(
        max_length=50, verbose_name="Отчество получателя", blank=True, null=True
    )
    last_name: models.CharField = models.CharField(
        max_length=50, verbose_name="Фамилия получателя", blank=True, null=True
    )
    comment: models.TextField = models.TextField(verbose_name="Комментарий", blank=True, null=True)

    def __str__(self) -> str:
        """Строковое отображение объекта получателя в соответствии со значением поля email"""

        result = f"{str(self.email)}"
        if self.first_name or self.middle_name or self.last_name:
            result += ": "
        result += " ".join([name for name in [self.last_name, self.first_name, self.middle_name] if name is not None])
        return result

    class Meta:
        """Класс настроек отображения получателя"""

        verbose_name = "Получатель"
        verbose_name_plural = "Получатели"
        ordering = ["email"]


class Message(models.Model):
    """Модель сообщения рассылки"""

    title: models.CharField = models.CharField(max_length=300, verbose_name="Тема сообщения")
    content: models.TextField = models.TextField(verbose_name="Содержание письма")
    author: models.ForeignKey = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="messages", verbose_name="Автор"
    )

    def __str__(self) -> str:
        """Строковое отображение объекта сообщения в виде его темы"""

        return str(self.title)

    class Meta:
        """Класс настроек отображения сообщения"""

        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ["title"]


class Mailing(models.Model):
    """Модель рассылки"""

    start_time: models.DateTimeField = models.DateTimeField(
        verbose_name="Начало рассылки", help_text="Укажите дату и время начала отправки писем."
    )
    end_time: models.DateTimeField = models.DateTimeField(
        verbose_name="Окончание рассылки",
        help_text="Укажите дату и время завершения отправки писем.",
    )
    STATUS_CHOICES = [("created", "Создана"), ("started", "Запущена"), ("completed", "Завершена")]
    status: models.CharField = models.CharField(
        max_length=9, choices=STATUS_CHOICES, default="created", verbose_name="Статус рассылки"
    )
    message: models.ForeignKey = models.ForeignKey(
        Message, on_delete=models.CASCADE, related_name="mailings", verbose_name="Сообщение"
    )
    recipients: models.ManyToManyField = models.ManyToManyField(
        Recipient, related_name="offers", verbose_name="Получатели", help_text="Выберите получателей рассылки"
    )

    def __str__(self) -> str:
        """Строковое представление рассылки в виде первых пяти слов темы ее сообщения"""

        return " ".join(self.message.title.split()[:5])

    class Meta:
        """Класс настроек отображения рассылки"""

        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        ordering = ["status", "message"]
        permissions = [("stop_mailing", "Может остановить рассылку")]


class Attempt(models.Model):
    """Модель попытки отправки письма получателю"""

    mailing: models.ForeignKey = models.ForeignKey(
        Mailing, on_delete=models.CASCADE, related_name="attempts", verbose_name="Рассылка"
    )
    recipient: models.ForeignKey = models.ForeignKey(
        Recipient, on_delete=models.CASCADE, related_name="attempts", verbose_name="Получатель"
    )
    send_time: models.DateTimeField = models.DateTimeField(
        verbose_name="Дата и время попытки", help_text="Дата и время попытки отправки "
    )
    STATUS_CHOICES = [("success", "Успешно"), ("fail", "Не успешно")]
    status: models.CharField = models.CharField(
        max_length=7, choices=STATUS_CHOICES, blank=True, null=True, default=None, verbose_name="Статус отправки"
    )
    server_response: models.TextField = models.TextField(verbose_name="Ответ сервера-получателя")

    def __str__(self) -> str:
        """Строковое представление попытки отправки письма получателю"""

        return f"{self.recipient.email}: {self.status}"

    class Meta:
        """Класс настроек отображения рассылки"""

        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылки"
        ordering = ["mailing", "recipient"]
