from typing import Any

from django.contrib import messages
from django.core.files.base import File
from django.forms import BaseForm
from django.http import FileResponse, HttpRequest, HttpResponse
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, FormView, ListView, TemplateView, UpdateView

from .forms import MailingForm, MessageForm, SingleRecipientForm, UploadRecipientListForm
from .models import Mailing, Message, Recipient
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
        """Вывод в шаблон списка существующих получателей
        и установка флага для отображения формы создания нового получателя рассылок"""

        context = super().get_context_data(**kwargs)
        context["object_list"] = Recipient.objects.all()
        context["form_exist"] = True
        return context


class RecipientUpdateView(UpdateView):
    """Контроллер редактирования информации о получателе"""

    model = Recipient
    form_class = SingleRecipientForm
    template_name = "distribution/recipient_list.html"
    success_url = reverse_lazy("distribution:recipients")

    def get_context_data(self, **kwargs: Any) -> dict:
        """Вывод в шаблон списка существующих получателей
        и установка флага для отображения формы редактирования информации о получателе рассылок"""

        context = super().get_context_data(**kwargs)
        context["object_list"] = Recipient.objects.all()
        context["form_exist"] = True
        return context


class RecipientDeleteView(DeleteView):
    """Контроллер удаления информации о получателе"""

    model = Recipient
    template_name = "distribution/recipient_list.html"
    success_url = reverse_lazy("distribution:recipients")

    def get_context_data(self, **kwargs: Any) -> dict:
        """Вывод в шаблон списка существующих получателей
        и установка флага для отображения формы удаления информации о получателе рассылок"""

        context = super().get_context_data(**kwargs)
        context["object_list"] = Recipient.objects.all()
        context["confirm_delete"] = True
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
        """Вывод в шаблон списка существующих получателей
        и установка флага для отображения формы загрузки excel-файла с информацией о получателях рассылок"""

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


class MessageListView(ListView):
    """Контроллер страницы списка сообщений"""

    model = Message


class MessageDetailView(DetailView):
    """Контроллер страницы одного сообщения"""

    model = Message

    def get_context_data(self, **kwargs: Any) -> dict:
        """Установка флага для отображения в шаблоне штатного набора действий"""

        context = super().get_context_data(**kwargs)
        context["normal_mode"] = True
        return context


class MessageCreateView(CreateView):
    """Контроллер создания сообщения рассылки"""

    model = Message
    form_class = MessageForm

    def get_success_url(self) -> str:
        """Редирект на страницу текущего сообщения после его создания"""

        self_object = self.object
        if isinstance(self_object, Message):
            return reverse("distribution:message_detail", kwargs={"pk": self_object.pk})
        return reverse("distribution:messages")


class MessageUpdateView(UpdateView):
    """Контроллер редактирования сообщения рассылки"""

    model = Message
    form_class = MessageForm

    def get_context_data(self, **kwargs: Any) -> dict:
        """Установка флага для отображения шаблона в режиме редактирования"""

        context = super().get_context_data(**kwargs)
        context["update_mode"] = True
        return context

    def get_success_url(self) -> str:
        """Редирект на страницу текущего сообщения после завершения редактирования"""

        self_object = self.object
        if isinstance(self_object, Message):
            return reverse("distribution:message_detail", kwargs={"pk": self_object.pk})
        return reverse("distribution:messages")


class MessageDeleteView(DeleteView):
    """Контроллер удаления сообщения рассылки"""

    model = Message
    template_name = "distribution/message_detail.html"
    success_url = reverse_lazy("distribution:messages")

    def get_context_data(self, **kwargs: Any) -> dict:
        """Установка флага для отображения шаблона в режиме удаления"""

        context = super().get_context_data(**kwargs)
        context["confirm_delete"] = True
        return context


class MailingListView(ListView):
    """Контроллер страницы списка рассылок"""

    model = Mailing


class MailingCreateView(CreateView):
    """Контроллер страницы создания рассылки"""

    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy("distribution:mailing_list")
