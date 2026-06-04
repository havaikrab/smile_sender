from argparse import ArgumentParser
from typing import Any

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.utils import timezone

from distribution.models import Mailing
from distribution.services import distribution_logger, send_mails


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
            send_mails(mailing)
