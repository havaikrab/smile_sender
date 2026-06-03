import os
import time
from argparse import ArgumentParser
from typing import Any

from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone

from config.settings import EMAIL_HOST_USER
from distribution.models import Attempt, Mailing
from distribution.services import distribution_logger


class Command(BaseCommand):
    help = "Запускает рассылку писем, для запуска необходимо указать id рассылки"

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Добавление флага, для передачи команде id рассылки"""

        parser.add_argument("--id", type=int, help="id рассылки из базы данных")

    @staticmethod
    def __check_readiness(mailing_id: int) -> Mailing:
        """Определяет готовность рассылки к запуску"""

        mailing = Mailing.objects.get(pk=mailing_id)
        if mailing.status != "created":
            raise ValueError(
                f'Запускаемая рассылка должна иметь статус "created". Текущий статус рассылки {mailing.status}.'
            )
        time_now = timezone.now()
        if mailing.start_time > time_now or mailing.end_time < time_now:
            raise ValueError("Рассылка не может быть запущена в настоящее время.")
        return mailing

    @staticmethod
    def __send_mails(mailing: Mailing) -> None:
        """Непосредственная отправка писем"""

        distribution_logger.info(f"Запущена рассылка id{mailing.pk}.")
        mailing.status = "started"
        mailing.save()
        recipients = mailing.recipients.all()
        success_count = 0
        fail_count = 0
        for recipient in recipients:
            try:
                send_mail(
                    mailing.message.title,
                    mailing.message.content,
                    from_email=EMAIL_HOST_USER,
                    recipient_list=[recipient.email],
                    fail_silently=False,
                )
                smtp_response = "250 OK: message accepted for delivery"
                status = "success"
                success_count += 1
            except Exception as exc:
                smtp_response = str(exc)
                status = "fail"
                distribution_logger.warning(f"Ошибка при обращении к SMTP-серверу: {exc}.")
                fail_count += 1
            Attempt.objects.create(mailing=mailing, recipient=recipient, status=status, server_response=smtp_response)
            time_to_sleep = int(os.getenv("SENDING_INTERVAL", 300))
            time.sleep(time_to_sleep)
        mailing.status = "completed"
        mailing.save()
        distribution_logger.info(
            f"Рассылка id{mailing.pk} завершена. Отправлено - {success_count}, не отправлено - {fail_count} писем."
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Запись данных приложения catalog в файл fixture/fixture_catalog.json"""

        mailing_id = options.get("id", 0)
        try:
            mailing = self.__check_readiness(mailing_id)
        except ObjectDoesNotExist:
            distribution_logger.error("Попытка запуска несуществующей рассылки.")
        except ValueError as exc:
            distribution_logger.error(f"{exc}")
        else:
            self.__send_mails(mailing)
