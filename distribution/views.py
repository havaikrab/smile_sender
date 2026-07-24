from typing import Any, Optional

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.core.files.base import File
from django.db.models import QuerySet
from django.forms import BaseForm
from django.http import FileResponse, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, FormView, ListView, TemplateView, UpdateView

from users.models import CustomUser
from users.services import CheckManagerMixin

from .forms import MailingForm, MessageForm, SingleRecipientForm, UploadRecipientListForm
from .models import Mailing, Message, Recipient
from .services import ExcelManager, get_cached_statistics, group_context
from .tasks import shared_send_mailing_task


class HomeView(CheckManagerMixin, TemplateView):
    """Контроллер главной страницы приложения distribution"""

    template_name = "distribution/home_page.html"

    def get_context_data(self, **kwargs: Any) -> dict:
        """Вывод в шаблон статистики приложения"""

        context = super().get_context_data(**kwargs)
        user = self.request.user
        context.update(get_cached_statistics(user))
        return context


class RecipientManagementListView(LoginRequiredMixin, PermissionRequiredMixin, CheckManagerMixin, ListView):
    """Контроллер страницы списка всех получателей, доступной только менеджерам приложения"""

    model = Recipient
    permission_required = ("distribution.view_recipient",)

    def get_context_data(self, **kwargs: Any) -> dict:
        """Установка флага для отображения шаблона без ссылок на действия с объектами получателей"""

        context = super().get_context_data(**kwargs)
        context["management"] = True
        return context


class RecipientListView(LoginRequiredMixin, CheckManagerMixin, ListView):
    """Контроллер страницы пользовательского списка получателей"""

    model = Recipient

    def get_queryset(self) -> QuerySet:
        """Определение личного списка получателей для каждого пользователя"""

        user = self.request.user
        if isinstance(user, CustomUser):
            return user.customers.all()
        raise PermissionDenied


class SingleRecipientCreateView(CheckManagerMixin, CreateView):
    """Контроллер добавления одного получателя рассылок через интерфейс приложения"""

    model = Recipient
    form_class = SingleRecipientForm
    success_url = reverse_lazy("distribution:recipients")

    def form_valid(self, form: SingleRecipientForm) -> HttpResponse:
        """Установка связи созданного объекта получателя с авторизованным пользователем"""

        recipient = form.save()
        user = self.request.user
        if isinstance(user, CustomUser):
            user.customers.add(recipient)
        return redirect(self.success_url)


class RecipientUpdateView(CheckManagerMixin, UpdateView):
    """Контроллер редактирования информации о получателе"""

    model = Recipient
    form_class = SingleRecipientForm
    template_name = "distribution/recipient_form.html"
    success_url = reverse_lazy("distribution:recipients")

    def get_object(self, queryset: Optional[QuerySet] = None) -> Recipient:
        """Проверка отношения получателя к зарегистрированному пользователю"""

        user = self.request.user
        recipient = super().get_object()
        if isinstance(user, CustomUser) and isinstance(recipient, Recipient) and user.customers.contains(recipient):
            return recipient
        raise PermissionDenied


class RecipientDeleteView(CheckManagerMixin, DeleteView):
    """Контроллер удаления информации о получателе"""

    model = Recipient
    template_name = "distribution/recipient_form.html"
    success_url = reverse_lazy("distribution:recipients")

    def get_object(self, queryset: Optional[QuerySet] = None) -> Recipient:
        """Проверка отношения получателя к зарегистрированному пользователю"""

        user = self.request.user
        recipient = super().get_object()
        if isinstance(user, CustomUser) and isinstance(recipient, Recipient) and user.customers.contains(recipient):
            return recipient
        raise PermissionDenied

    def get_context_data(self, **kwargs: Any) -> dict:
        """Установка флага для отображения формы удаления информации о получателе рассылок"""

        context = super().get_context_data(**kwargs)
        context["confirm_delete"] = True
        return context


class DownloadRecipientsFormView(View):
    """Контроллер ссылки для скачивания формы списка получателей"""

    def get(self, request: HttpRequest) -> FileResponse:
        """Передача файла формы в ответ сервера"""

        return ExcelManager.send_excel_form()


class UploadRecipientListView(LoginRequiredMixin, CheckManagerMixin, FormView):
    """Контроллер загрузки информации о получателях из excel-файла"""

    form_class = UploadRecipientListForm
    template_name = "distribution/recipient_form.html"
    success_url = reverse_lazy("distribution:recipients")

    def form_valid(self, form: BaseForm) -> HttpResponse:
        """Чтение загруженного файла и запись данных в БД"""

        file = self.request.FILES.get("excel_file")
        user = self.request.user
        if isinstance(file, File) and isinstance(user, CustomUser):
            data_manager = ExcelManager(user, form, file)
            try:
                data_manager.check_file()
            except KeyError:
                return super().form_invalid(form)
            new_recipients = data_manager.create_recipients()
            data_manager.set_user_customers_relations(new_recipients)
            if len(data_manager.report["success_operations"]) > 0:
                messages.success(self.request, "\n".join(data_manager.report["success_operations"]))
            if len(data_manager.report["existing_objects"]) > 0:
                messages.warning(self.request, "\n".join(data_manager.report["existing_objects"]))
            if len(data_manager.report["invalid_rows"]) > 0:
                error_str = ", ".join(data_manager.report["invalid_rows"])
                messages.error(self.request, f"Строки, содержащие некорректные данные:\n{error_str}.")
            return super().form_valid(form)
        return super().form_invalid(form)


class MessageListView(LoginRequiredMixin, CheckManagerMixin, ListView):
    """Контроллер страницы списка сообщений"""

    model = Message

    def get_queryset(self) -> QuerySet:
        """Отображение пользователю только тех писем, автором которых он является"""

        user = self.request.user
        if isinstance(user, CustomUser):
            return user.messages.all()
        raise PermissionDenied


class MessageDetailView(LoginRequiredMixin, CheckManagerMixin, DetailView):
    """Контроллер страницы одного сообщения"""

    model = Message

    def get_object(self, queryset: Optional[QuerySet] = None) -> Message:
        """Проверка, является ли зарегистрированный пользователь автором письма"""

        user = self.request.user
        message = super().get_object()
        if isinstance(user, CustomUser) and isinstance(message, Message) and message.author == user:
            return message
        raise PermissionDenied


class MessageCreateView(LoginRequiredMixin, CheckManagerMixin, CreateView):
    """Контроллер создания сообщения рассылки"""

    model = Message
    form_class = MessageForm

    def get_success_url(self) -> str:
        """Редирект на страницу текущего сообщения после его создания"""

        self_object = self.object
        if isinstance(self_object, Message):
            return reverse("distribution:message_detail", kwargs={"pk": self_object.pk})
        return reverse("distribution:messages")

    def form_valid(self, form: MessageForm) -> HttpResponse:
        """Указание авторизованного пользователя в качестве автора письма"""

        form.instance.author = self.request.user
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, CheckManagerMixin, UpdateView):
    """Контроллер редактирования сообщения рассылки"""

    model = Message
    form_class = MessageForm

    def get_object(self, queryset: Optional[QuerySet] = None) -> Message:
        """Проверка, является ли зарегистрированный пользователь автором письма"""

        user = self.request.user
        message = super().get_object()
        if isinstance(user, CustomUser) and isinstance(message, Message) and message.author == user:
            return message
        raise PermissionDenied

    def get_success_url(self) -> str:
        """Редирект на страницу текущего сообщения после завершения редактирования"""

        self_object = self.object
        if isinstance(self_object, Message):
            return reverse("distribution:message_detail", kwargs={"pk": self_object.pk})
        return reverse("distribution:messages")


class MessageDeleteView(LoginRequiredMixin, CheckManagerMixin, DeleteView):
    """Контроллер удаления сообщения рассылки"""

    model = Message
    template_name = "distribution/message_detail.html"
    success_url = reverse_lazy("distribution:messages")

    def get_object(self, queryset: Optional[QuerySet] = None) -> Message:
        """Проверка, является ли зарегистрированный пользователь автором письма"""

        user = self.request.user
        message = super().get_object()
        if isinstance(user, CustomUser) and isinstance(message, Message) and message.author == user:
            return message
        raise PermissionDenied

    def get_context_data(self, **kwargs: Any) -> dict:
        """Установка флага для отображения шаблона в режиме удаления"""

        context = super().get_context_data(**kwargs)
        context["confirm_delete"] = True
        return context


class MailingCreateView(LoginRequiredMixin, CheckManagerMixin, CreateView):
    """Контроллер страницы создания рассылки"""

    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy("distribution:mailing_list")

    def get_form_kwargs(self) -> dict:
        """Передача в форму списка созданных пользователем писем"""

        kwargs = super().get_form_kwargs()
        user = self.request.user
        if isinstance(user, CustomUser):
            kwargs["user_messages"] = Message.objects.filter(author=user)
        return kwargs


class MailingListView(LoginRequiredMixin, CheckManagerMixin, ListView):
    """Контроллер страницы списка рассылок"""

    model = Mailing

    def get_queryset(self) -> QuerySet:
        """Отображение пользователю только его собственных рассылок"""

        user = self.request.user
        return super().get_queryset().filter(message__author=user)

    def get_context_data(self, **kwargs: Any) -> dict:
        """Передача в шаблон словаря сгруппированных по значению статуса объектов рассылок"""

        context = super().get_context_data(**kwargs)
        context["sorted_objects"] = group_context(context["object_list"])
        return context


class MailingManagementListView(LoginRequiredMixin, PermissionRequiredMixin, CheckManagerMixin, ListView):
    """Контроллер страницы всех рассылок, доступна только менеджерам приложения"""

    model = Mailing
    permission_required = ("distribution.view_mailing",)

    def get_context_data(self, **kwargs: Any) -> dict:
        """Передача в шаблон словаря сгруппированных по значению статуса объектов рассылок"""

        context = super().get_context_data(**kwargs)
        context["sorted_objects"] = group_context(context["object_list"])
        return context


class MailingDetailView(LoginRequiredMixin, CheckManagerMixin, DetailView):
    """Контроллер страницы рассылки"""

    model = Mailing

    def get_object(self, queryset: Optional[QuerySet] = None) -> Mailing:
        """Ограничение доступа к странице пользователям, не являющимися автором сообщения или менеджером приложения"""

        mailing = super().get_object()
        user = self.request.user
        if isinstance(user, CustomUser) and isinstance(mailing, Mailing):
            if mailing.message.author == user or user.has_perm("distribution.view_mailing"):
                return mailing
        raise PermissionDenied

    def get_context_data(self, **kwargs: Any) -> dict:
        """Установка флагов для отображения шаблона в штатном режиме и отображения кнопки для остановки рассылки"""

        context = super().get_context_data(**kwargs)
        if self.object.start_time <= timezone.now() <= self.object.end_time and self.object.status == "created":
            context["ready"] = True
        key = f"continue_mailing_{self.object.pk}"
        continue_flag = cache.get(key)
        if continue_flag == "continue":
            context["stop_button"] = True
        context["normal_mode"] = True
        return context


class MailingUpdateView(LoginRequiredMixin, CheckManagerMixin, UpdateView):
    """Контроллер страницы редактирования рассылки"""

    model = Mailing
    form_class = MailingForm

    def get_object(self, queryset: Optional[QuerySet] = None) -> Mailing:
        """Ограничение доступа к странице пользователям, не являющимися автором сообщения"""

        mailing = super().get_object()
        user = self.request.user
        if (
            isinstance(user, CustomUser)
            and isinstance(mailing, Mailing)
            and mailing.status == "created"
            and mailing.message.author == user
        ):
            return mailing
        raise PermissionDenied

    def get_form_kwargs(self) -> dict:
        """Передача в форму списка созданных пользователем писем"""

        kwargs = super().get_form_kwargs()
        user = self.request.user
        if isinstance(user, CustomUser):
            kwargs["user_messages"] = Message.objects.filter(author=user)
        return kwargs

    def get_success_url(self) -> str:
        """Редирект на страницу текущей рассылки после завершения редактирования"""

        self_object = self.object
        if isinstance(self_object, Mailing):
            return reverse("distribution:mailing_detail", kwargs={"pk": self_object.pk})
        return reverse("distribution:mailing_list")


class MailingDeleteView(LoginRequiredMixin, CheckManagerMixin, DeleteView):
    """Контроллер удаления рассылки"""

    model = Mailing
    template_name = "distribution/mailing_detail.html"
    success_url = reverse_lazy("distribution:mailing_list")

    def get_object(self, queryset: Optional[QuerySet] = None) -> Mailing:
        """Ограничение доступа к странице рассылки пользователям, не являющимися автором сообщения"""

        mailing = super().get_object()
        user = self.request.user
        if (
            isinstance(user, CustomUser)
            and isinstance(mailing, Mailing)
            and mailing.status != "started"
            and mailing.message.author == user
        ):
            return mailing
        raise PermissionDenied

    def get_context_data(self, **kwargs: Any) -> dict:
        """Установка флага для отображения шаблона в режиме удаления"""

        context = super().get_context_data(**kwargs)
        context["confirm_delete"] = True
        return context


class MailingStartView(LoginRequiredMixin, View):
    """Контроллер запуска процесса рассылки писем"""

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        """Получение команды на запуск рассылки и ее запуск"""

        mailing = get_object_or_404(Mailing, pk=pk)
        user = self.request.user
        if mailing.status != "created":
            messages.error(request, f"Рассылка со статусом {mailing.status} не может быть запущена повторно.")
            return redirect("distribution:mailing_detail", pk=pk)
        if not isinstance(user, CustomUser) or mailing.message.author != user or user.is_blocked:
            raise PermissionDenied
        shared_send_mailing_task.delay(pk)
        messages.success(request, f'Рассылка "{mailing.message.title}" запущена')
        return redirect("distribution:mailing_list", pk=pk)


class MailingStopView(LoginRequiredMixin, View):
    """Контроллер остановки процесса рассылки писем"""

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        """Получение команды на остановку рассылки и установка в кеше отметки о ее завершении"""

        mailing = get_object_or_404(Mailing, pk=pk)
        user = self.request.user
        if (
            isinstance(user, CustomUser)
            and mailing.message.author != user
            and not user.has_perm("distribution.stop_mailing")
        ):
            raise PermissionDenied
        key = f"continue_mailing_{mailing.pk}"
        time_to_end = mailing.end_time - timezone.now()
        time_to_life = time_to_end.total_seconds()
        cache_status = cache.get(key)
        if cache_status == "continue":
            cache.set(key, "stopped", time_to_life)
        messages.success(request, f'Рассылка "{mailing.message.title}" остановлена.')
        return redirect("distribution:mailing_detail", pk=pk)
