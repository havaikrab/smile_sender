from typing import Any

from django.contrib import messages
from django.core.files.base import File
from django.forms import BaseForm
from django.http import FileResponse, HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, FormView, ListView, TemplateView

from .forms import SingleRecipientForm, UploadRecipientListForm
from .models import Message, Recipient
from .services import ExcelManager


class HomeView(TemplateView):
    """Контроллер главной страницы приложения distribution"""

    template_name = "distribution/home_page.html"


class RecipientListView(ListView):
    """Контроллер страницы списка получателей"""

    model = Recipient


class SingleRecipientCreateView(CreateView):
    """Контроллер добавления одного получателя рассылок через интерфейс приложения"""

    model = Recipient
    form_class = SingleRecipientForm
    template_name = "distribution/recipient_list.html"
    success_url = reverse_lazy("distribution:recipients")

    def get_context_data(self, **kwargs: Any) -> dict:
        """Вывод в шаблон списка существующих получателей"""

        context = super().get_context_data(**kwargs)
        context["object_list"] = Recipient.objects.all()
        context["form_exist"] = True
        return context


class DownloadRecipientsFormView(View):
    """Контроллер ссылки для скачивания формы списка получателей"""

    def get(self, request: HttpRequest) -> FileResponse:
        """Передача файла формы в ответ сервера"""

        return ExcelManager.send_excel_form()


class UploadRecipientListView(FormView):
    """Контроллер загрузки информации о получателях из excel-файла"""

    form_class = UploadRecipientListForm
    template_name = "distribution/recipient_list.html"
    success_url = reverse_lazy("distribution:recipients")

    def get_context_data(self, **kwargs: Any) -> dict:
        """Вывод в шаблон списка существующих получателей"""

        context = super().get_context_data(**kwargs)
        context["object_list"] = Recipient.objects.all()
        context["upload_exist"] = True
        return context

    def form_valid(self, form: BaseForm) -> HttpResponse:
        """Чтение загруженного файла и запись данных в БД"""

        file = self.request.FILES.get("excel_file")
        if isinstance(file, File):
            data_manager = ExcelManager(form, file)
            try:
                data_manager.check_file()
            except KeyError:
                return super().form_invalid(form)
            data_manager.create_recipients()
            if len(data_manager.report["success_operations"]) > 0:
                messages.success(self.request, "\n".join(data_manager.report["success_operations"]))
            if len(data_manager.report["existing_objects"]) > 0:
                messages.warning(self.request, "\n".join(data_manager.report["existing_objects"]))
            if len(data_manager.report["invalid_rows"]) > 0:
                error_str = ", ".join(data_manager.report["invalid_rows"])
                messages.error(self.request, f"Строки, содержащие некорректные данные:\n{error_str}.")
            return super().form_valid(form)
        return super().form_invalid(form)


class MessageCreateView(CreateView):
    """Контроллер создания сообщения рассылки"""

    model = Message
