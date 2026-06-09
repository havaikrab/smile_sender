from typing import Any

from django.core.management.base import BaseCommand
from django.utils import timezone

from distribution.models import Mailing


class Command(BaseCommand):
    help = "Показывает все готовые к запуску рассылки"

    @staticmethod
    def __prepare_queryset() -> list:
        """Определяет объекты рассылок, готовых к запуску"""

        mailing_list = Mailing.objects.filter(status="created")
        time_now = timezone.now()
        return [mailing for mailing in mailing_list if mailing.start_time <= time_now <= mailing.end_time]

    def handle(self, *args: Any, **options: Any) -> None:
        """Выводит в консоль информацию о рассылках, готовых к запуску"""

        mailing_list = self.__prepare_queryset()
        print("\nСписок рассылок, готовых к запуску:\n")
        for mailing in mailing_list:
            print(f"""id - {mailing.pk}.
Период: {timezone.localtime(mailing.start_time)} - {timezone.localtime(mailing.end_time)}.
Тема: {mailing.message}.\n""")
