from django.db import models

class Recipient(models.Model):
    """Модель получателя рассылки"""

    email = models.EmailField(unique=True, verbose_name='Электронная почта получателя')
    first_name = models.CharField(max_length=50, verbose_name='Имя получателя', blank=True, null=True)
    middle_name = models.CharField(max_length=50, verbose_name='Отчество получателя', blank=True, null=True)
    last_name = models.CharField(max_length=50, verbose_name='Фамилия получателя', blank=True, null=True)
    comment = models.TextField(verbose_name='Комментарий', blank=True, null=True)

    def __str__(self):
        """Строковое отображение объекта получателя в соответствии со значением поля email"""

        return self.email

    class Meta:
        """Класс настроек отображения получателя"""

        verbose_name = 'Получатель'
        verbose_name_plural = 'Получатели'
        ordering = ['email']


class Message(models.Model):
    """Модель сообщения рассылки"""

    title = models.CharField(max_length=300, verbose_name='Тема сообщения')
    content = models.TextField(verbose_name='Содержание письма')

    def __str__(self):
        """Строковое отображение объекта сообщения в виде его темы"""

        return self.title

    class Meta:
        """Класс настроек отображения сообщения"""

        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['title']


class Mailing(models.Model):
    """Модель рассылки"""

    start_time = models.DateTimeField(verbose_name='Начало рассылки', help_text='Дата и время начала отправки писем, установленное отправителем.')
    end_time = models.DateTimeField(verbose_name='Окончание рассылки', help_text='Дата и время окончания отправки писем, установленное отправителем.')
    STATUS_CHOICES = [('created', 'Создана'), ('started', 'Запущена'), ('completed', 'Завершена')]
    status = models.CharField(max_length=9, choices=STATUS_CHOICES, default='created', verbose_name='Статус рассылки')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='mailings', verbose_name='Сообщение')
    recipients = models.ManyToManyField(Recipient, related_name='mailings', verbose_name='Получатели')

    def __str__(self):
        """Строковое представление рассылки в виде первых пяти слов темы ее сообщения"""

        return ' '.join(self.message.title.split()[:5])

    class Meta:
        """Класс настроек отображения рассылки"""

        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        ordering = ['status', 'message']


class Attempt(models.Model):
    """Модель попытки отправки письма получателю"""

    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, related_name='attempts', verbose_name='Рассылка')
    recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE, related_name='attempts', verbose_name='Получатель')
    send_time = models.DateTimeField(auto_now_add= True, verbose_name='Дата и время попытки', help_text='Дата и время попытки отправки ')
    STATUS_CHOICES = [('success', 'Успешно'), ('fail', 'Не успешно')]
    status = models.CharField(max_length=7, choices=STATUS_CHOICES, blank=True, null=True, default=None, verbose_name='Статус отправки')
    server_response = models.TextField(verbose_name='Ответ сервера-получателя')

    def __str__(self):
        """Строковое представление попытки отправки письма получателю"""

        return f'{self.recipient.email}: {self.status}'

    class Meta:
        """Класс настроек отображения рассылки"""

        verbose_name = 'Попытка рассылки'
        verbose_name_plural = 'Попытки рассылки'
        ordering = ['mailing', 'recipient']
