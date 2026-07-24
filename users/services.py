from typing import Any

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.views.generic.base import ContextMixin

from config.settings import EMAIL_HOST_USER, SITE_URL
from distribution.services import distribution_logger
from users.models import CustomUser


class CheckManagerMixin(ContextMixin):
    """Класс-миксин, проверяющий, входит ли пользователь в группу менеджеров"""

    def get_context_data(self: Any, **kwargs: Any) -> dict:
        """Передача в шаблон флага, если пользователь является менеджером"""

        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.groups.filter(name="manager").exists():
            context["manager"] = True
        return context


def send_activate_link(user: CustomUser) -> None:
    """Отправляет только что зарегистрировавшемуся пользователю ссылку для активации аккаунта"""

    token = default_token_generator.make_token(user)
    activation_link = f"{SITE_URL}{reverse('users:activate', kwargs={'pk': user.pk, 'token': token})}"
    message = f"""Вы зарегистрировались в Smile Sender, для активации аккаунта и первого логина перейдите по ссылке
{activation_link}"""
    try:
        send_mail("Активация аккаунта Smile Sender", message, EMAIL_HOST_USER, [user.email], fail_silently=False)
        distribution_logger.info(f"Отправлена ссылка для активации аккаунта на {user.email}.")
    except Exception as exc:
        distribution_logger.error(
            f'Ошибка "{exc}" при попытке отправить ссылку для активации аккаунта на {user.email}.'
        )
