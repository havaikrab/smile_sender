from argparse import ArgumentParser
from typing import Any

from django.core.management.base import BaseCommand

from distribution.services import execute_mailing


class Command(BaseCommand):
    help = "Запускает рассылку писем, для запуска необходимо указать id рассылки"

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Добавление флага, для передачи команде id рассылки"""

        parser.add_argument("--id", type=int, help="id рассылки из базы данных")

    def handle(self, *args: Any, **options: Any) -> None:
        """Запись данных приложения catalog в файл fixture/fixture_catalog.json"""

        mailing_id = options.get("id", 0)
        execute_mailing(mailing_id)
