import logging
import os
from io import BytesIO

import openpyxl
from django.core.exceptions import ValidationError
from django.core.files.base import File
from django.db.models import QuerySet
from django.forms import BaseForm
from django.http import FileResponse
from django.utils import timezone
from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet

from distribution.models import Mailing, Recipient

distribution_logger = logging.getLogger("distribution_logger")
os.makedirs("logs/", exist_ok=True)
file_handler = logging.FileHandler("logs/distribution_logger.log", mode="a", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
distribution_logger.addHandler(file_handler)
distribution_logger.setLevel(logging.INFO)


class ExcelManager:
    """Класс работы с Excel-файлами"""

    __columns = {
        "A": "email",
        "B": "first_name",
        "C": "middle_name",
        "D": "last_name",
        "E": "comment",
    }

    def __init__(self, form: BaseForm, excel_file: File):
        """Создание менеджера для загружаемого excel-файла"""

        self.__file = excel_file
        self.__form = form
        self.__sheet = Workbook().active
        self.report: dict = {"success_operations": list(), "existing_objects": list(), "invalid_rows": list()}

    def check_file(self) -> None:
        """Проверка корректности структуры загружаемого файла"""

        data = openpyxl.load_workbook(self.__file)
        if "recipients" not in data.sheetnames:
            self.__form.add_error("excel_file", 'Файл должен содержать лист "recipients"')
            raise KeyError
        sheet = data["recipients"]
        for k, v in ExcelManager.__columns.items():
            if sheet[f"{k}1"].value != v:
                self.__form.add_error("excel_file", 'Лист "recipients" содержит некорректные названия столбцов')
                raise KeyError
        self.__sheet = sheet

    def create_recipients(self) -> None:
        """Запись информации о получателях рассылок в БД"""

        if isinstance(self.__sheet, Worksheet):
            existing_emails = list(Recipient.objects.all().values_list("email", flat=True))
            uploaded_emails = set([self.__sheet[f"A{row}"].value for row in range(2, self.__sheet.max_row + 1)])
            new_emails = uploaded_emails.difference(existing_emails)
            new_emails.discard(None)
            new_emails.discard("")
            valid_recipients = list()
            for row in range(2, self.__sheet.max_row + 1):
                recipient_dict = {v: self.__sheet[f"{k}{row}"].value for k, v in ExcelManager.__columns.items()}
                row_email = recipient_dict["email"]
                if row_email in new_emails:
                    try:
                        recipient = Recipient(**recipient_dict)
                        recipient.full_clean()
                        valid_recipients.append(recipient)
                        self.report["success_operations"].append(
                            f"Получатель №{row} с email {row_email} добавлен в базу данных"
                        )
                    except ValidationError:
                        self.report["invalid_rows"].append(str(row))
                    new_emails.discard(row_email)
                else:
                    if row_email is not None and row_email != "":
                        self.report["existing_objects"].append(
                            f"Получатель №{row} с email {row_email} уже существует в базе данных"
                        )
            Recipient.objects.bulk_create(valid_recipients, ignore_conflicts=True)

    @staticmethod
    def send_excel_form() -> FileResponse:
        """Подготавливает к отправке стандартную excel-форму списка получателей"""

        new_excel = Workbook()
        current_sheet = new_excel.active
        if isinstance(current_sheet, Worksheet):
            current_sheet.title = "recipients"
            current_sheet.append(("email", "first_name", "middle_name", "last_name", "comment"))
        buffer = BytesIO()
        new_excel.save(buffer)
        buffer.seek(0)

        response = FileResponse(
            buffer,
            as_attachment=True,
            filename="recipients_form.xlsx",
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        return response


def group_context(queryset: QuerySet[Mailing]) -> dict:
    """Сортирует список объектов рассылок в соответствии со статусом"""

    time_now = timezone.now()
    sorted_context: dict[str, list] = {"created": list(), "ready": list(), "started": list(), "completed": list()}
    for mailing in queryset:
        if mailing.end_time < time_now or mailing.status == "completed":
            mailing.status = "completed"
            sorted_context["completed"].append(mailing)
        elif mailing.status == "started":
            sorted_context["started"].append(mailing)
        elif mailing.start_time <= time_now <= mailing.end_time:
            sorted_context["ready"].append(mailing)
        else:
            sorted_context["created"].append(mailing)
        Mailing.objects.bulk_update(sorted_context["completed"], ["status"])
    return sorted_context
