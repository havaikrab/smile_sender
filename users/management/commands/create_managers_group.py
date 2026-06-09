from typing import Any

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Создает в базе данных группу пользователей с названием manager и наделяет ее необходимыми правами"

    PERMISSIONS = [
        "view_recipient",
        "view_mailing",
        "view_customuser",
        "block_customuser",
        "unblock_customuser",
        "stop_mailing",
    ]

    @staticmethod
    def __create_manager_group() -> Group:
        """Проверяет наличие или создает группу пользователей с названием manager"""

        group, created = Group.objects.get_or_create(name="manager")
        if created:
            print('Группа "manager" создана.')
        else:
            print('Группа "manager" уже существует.')
        return group

    def handle(self, *args: Any, **options: Any) -> None:
        """Создает группу пользователей с необходимыми правами"""

        managers = self.__create_manager_group()
        managers.permissions.add(*[Permission.objects.get(codename=permission) for permission in self.PERMISSIONS])
        print('Группа "manager" получила необходимые права')
