from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Запускает рассылку писем, для запуска необходимо указать id рассылки"
