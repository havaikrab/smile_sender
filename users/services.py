from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail

from config.settings import EMAIL_HOST_USER, SITE_URL
from distribution.services import distribution_logger
from users.models import CustomUser


def send_activate_link(user: CustomUser) -> None:
    """Отправляет только что зарегистрировавшемуся пользователю ссылку для активации аккаунта"""

    token = default_token_generator.make_token(user)
    activation_link = f"{SITE_URL}/users/activate/{user.pk}/{token}/"
    message = f"""Вы зарегистрировались в Smile Sender, для активации аккаунта и первого логина перейдите по ссылке
{activation_link}"""
    try:
        send_mail("Активация аккаунта Smile Sender", message, EMAIL_HOST_USER, [user.email], fail_silently=False)
        distribution_logger.info(f"Отправлена ссылка для активации аккаунта на {user.email}.")
    except Exception as exc:
        distribution_logger.error(
            f'Ошибка "{exc}" при попытке отправить ссылку для активации аккаунта на {user.email}.'
        )
