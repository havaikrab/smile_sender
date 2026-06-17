from typing import Any, Optional

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import AbstractBaseUser, AnonymousUser, Group
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordChangeView, PasswordResetConfirmView, PasswordResetView
from django.db.models import QuerySet
from django.http import Http404, HttpRequest
from django.http.response import HttpResponse, HttpResponseBase, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, FormView, ListView, UpdateView

from distribution.services import distribution_logger

from .forms import (
    AssignGroupForm,
    CustomUserCreationForm,
    CustomUserDeleteForm,
    CustomUserPasswordChangeForm,
    CustomUserPasswordResetForm,
    CustomUserPasswordSetForm,
    CustomUserUpdateForm,
    SetCustomUserGroupForm,
)
from .models import CustomUser
from .services import CheckManagerMixin, send_activate_link


class CustomUserRegisterView(CreateView):
    """Контроллер страницы регистрации нового пользователя"""

    template_name = "users/register.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("distribution:main")

    def form_valid(self, form: CustomUserCreationForm) -> HttpResponseRedirect:
        """Отправка письма на email, указанный при регистрации, для активации аккаунта"""

        user = form.save()
        send_activate_link(user)
        messages.success(
            self.request,
            f"""Вы успешно зарегистрировались в Smile Sender,
на ваш email {user.email} отправлена ссылка для активации аккаунта, пожалуйста, перейдите по ней в ближайшее время.""",
        )
        distribution_logger.info(f"Зарегистрирован новый аккаунт на {user.email}.")
        return redirect(self.success_url)


class CustomUserActivationView(View):
    """Контроллер перехода по ссылке активации аккаунта"""

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseRedirect:
        """Проверка актуальности токена, переданного через url"""

        token = kwargs.get("token")
        pk = kwargs.get("pk")
        user = get_object_or_404(CustomUser, pk=pk)
        if user is not None:
            if default_token_generator.check_token(user, token):
                user.is_active = True
                user.save()
                messages.success(self.request, "Аккаунт активирован")
                login(request, user)
                distribution_logger.info(f'Аккаунт "{user.email}" успешно активирован')
            else:
                messages.error(self.request, "Ссылка для активации не действительна")
                distribution_logger.warning(f'Попытка активации аккаунта "{user.email}" c недействительным токеном')
        else:
            distribution_logger.error("Попытка активировать несуществующий аккаунт пользователя")
            messages.error(self.request, "Ссылка для активации не действительна")
        return redirect(reverse("distribution:main"))


class CustomUserProfileView(LoginRequiredMixin, CheckManagerMixin, DetailView):
    """Контроллер страницы профиля пользователя"""

    model = CustomUser

    def get_object(self, queryset: Optional[QuerySet] = None) -> AbstractBaseUser | AnonymousUser:
        """Определение объекта авторизованного пользователя"""

        return self.request.user


class CustomUserUpdateView(LoginRequiredMixin, CheckManagerMixin, UpdateView):
    """Контроллер страницы редактирования личных данных пользователя"""

    template_name = "users/customuser_detail.html"
    form_class = CustomUserUpdateForm
    success_url = reverse_lazy("users:profile")

    def get_object(self, queryset: Optional[QuerySet] = None) -> AbstractBaseUser | AnonymousUser:
        """Определение объекта авторизованного пользователя"""

        return self.request.user

    def get_context_data(self, **kwargs: Any) -> dict:
        """Добавление флага для отображения шаблона в режиме обновления данных"""

        context = super().get_context_data(**kwargs)
        context["update"] = True
        return context


class CustomUserPasswordChangeView(LoginRequiredMixin, CheckManagerMixin, PasswordChangeView):
    """Контроллер страницы смены пароля от аккаунта"""

    template_name = "users/customuser_detail.html"
    form_class = CustomUserPasswordChangeForm
    success_url = reverse_lazy("users:profile")

    def get_context_data(self, **kwargs: Any) -> dict:
        """Добавление флага для отображения шаблона в режиме смены пароля"""

        context = super().get_context_data(**kwargs)
        context["password_change"] = True
        return context


class CustomUserDeleteView(LoginRequiredMixin, CheckManagerMixin, DeleteView):
    """Контроллер страницы подтверждения удаления аккаунта"""

    template_name = "users/customuser_detail.html"
    form_class = CustomUserDeleteForm
    success_url = reverse_lazy("distribution:main")

    def get_object(self, queryset: Optional[QuerySet] = None) -> AbstractBaseUser | AnonymousUser:
        """Определение объекта удаляемого пользователя"""

        return self.request.user

    def get_context_data(self, **kwargs: Any) -> dict:
        """Добавление флага для отображения шаблона в режиме удаления аккаунта"""

        context = super().get_context_data(**kwargs)
        context["delete_profile"] = True
        return context

    def form_valid(self, form: CustomUserDeleteForm) -> HttpResponse:
        """Добавление лога и сообщения в шаблон об удалении аккаунта"""

        messages.success(self.request, "Ваш аккаунт был удален")
        distribution_logger.info(f"Аккаунт, зарегистрированный на {self.object.email}, был удален.")
        return super().form_valid(form)


class CustomUserPasswordResetView(PasswordResetView):
    """Контроллер ссылки для сброса пароля от аккаунта, для его дальнейшего восстановления"""

    template_name = "users/login.html"
    form_class = CustomUserPasswordResetForm
    success_url = reverse_lazy("distribution:main")

    def get_context_data(self, **kwargs: Any) -> dict:
        """Добавление флага для отображения шаблона в режиме сброса пароля от аккаунта"""

        context = super().get_context_data(**kwargs)
        context["reset_password"] = True
        return context


class CustomUserPasswordRemakeView(PasswordResetConfirmView):
    """Контроллер страницы переопределения пароля от аккаунта"""

    template_name = "users/login.html"
    form_class = CustomUserPasswordSetForm
    success_url = reverse_lazy("distribution:main")

    def get_context_data(self, **kwargs: Any) -> dict:
        """Добавление флага для отображения шаблона в режиме переопределения пароля от аккаунта"""

        context = super().get_context_data(**kwargs)
        context["remake_password"] = True
        return context

    def form_valid(self, form: SetPasswordForm) -> HttpResponse:
        """Добавление лога и сообщения в шаблон об удалении аккаунта"""

        messages.success(self.request, "Пароль был успешно изменен")
        if isinstance(self.user, CustomUser):
            distribution_logger.info(f"Пароль аккаунта, зарегистрированного на {self.user.email}, был изменен.")
        else:
            distribution_logger.warning("Попытка переустановить пароль у несуществующего аккаунта")
        return super().form_valid(form)


class CustomUserListView(LoginRequiredMixin, PermissionRequiredMixin, CheckManagerMixin, ListView):
    """Контроллер страницы всех зарегистрированных пользователей"""

    model = CustomUser
    permission_required = ("users.view_customuser",)


class CustomUserChangeBlockedStatusView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """Контроллер функции изменения статуса блокировки пользователя"""

    permission_required = ("users.block_customuser", "users.unblock_customuser")

    def post(self, request: HttpRequest, pk: int, mailing_pk: Optional[int] = None) -> HttpResponse:
        """Получение команды на изменение статуса блокировки пользователя"""

        manager = request.user
        user = get_object_or_404(CustomUser, pk=pk)
        if mailing_pk is not None:
            next_page = redirect("distribution:mailing_detail", pk=mailing_pk)
        else:
            next_page = redirect("users:users_list")
        if manager == user:
            messages.error(request, "Нельзя самостоятельно заблокировать или разблокировать собственный аккаунт")
            return next_page
        user.is_blocked = not user.is_blocked
        user.save()
        if user.is_blocked:
            distribution_logger.warning(f"Пользователь с e-mail {user.email} заблокирован.")
        else:
            distribution_logger.info(f"Пользователь с e-mail {user.email} разблокирован.")
        return next_page


class SetCustomUserGroupView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    """Контроллер страницы добавления пользователя в определенную группу персонала"""

    form_class = SetCustomUserGroupForm
    template_name = "users/set_user_group.html"
    success_url = reverse_lazy("users:users_list")
    permission_required = ("auth.change_group",)

    def get_context_data(self, **kwargs: Any) -> dict:
        """Передача в шаблон заголовка страницы"""

        context = super().get_context_data(**kwargs)
        context["header"] = "Назначение пользователя на должность"
        return context

    def form_valid(self, form: SetCustomUserGroupForm) -> HttpResponse:
        """Определение пользователя в выбранные группы персонала"""

        user_pk = self.kwargs.get("pk")
        user = CustomUser.objects.get(pk=user_pk)
        groups = form.cleaned_data.get("groups")
        if isinstance(groups, QuerySet):
            user.groups.add(*groups)
        return redirect("users:users_list")


class GroupListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """Контроллер страницы списка групп пользователей"""

    model = Group
    template_name = "users/group_list.html"
    permission_required = ("auth.view_group",)


class AssignGroupView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    """Контроллер страницы добавления нескольких пользователей в определенную группу"""

    form_class = AssignGroupForm
    template_name = "users/set_user_group.html"
    success_url = reverse_lazy("users:users_list")
    permission_required = ("auth.change_group",)

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseBase:
        """Сохранение объекта группы в атрибут класса"""

        group_id = self.kwargs.get("pk")
        self.group = get_object_or_404(Group, id=group_id)
        view_action = self.kwargs.get("action")
        if view_action == "assign":
            self.view_action = "assign"
        elif view_action == "exclude":
            self.view_action = "exclude"
        else:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict:
        """Передача в шаблон заголовка страницы"""

        context = super().get_context_data(**kwargs)
        if self.view_action == "assign":
            context["header"] = f"Добавление пользователей в группу {self.group.name}"
        else:
            context["header"] = f"Исключение пользователей из группы {self.group.name}"
        return context

    def get_form_kwargs(self) -> dict:
        """Передача в форму списка пользователей, не состоящих в группе"""

        kwargs = super().get_form_kwargs()
        if self.view_action == "assign":
            kwargs["users_list"] = CustomUser.objects.exclude(groups=self.group)
            kwargs["view_action"] = "assign"

        else:
            kwargs["users_list"] = self.group.user_set.all()
            kwargs["view_action"] = "exclude"
        return kwargs

    def form_valid(self, form: SetCustomUserGroupForm) -> HttpResponse:
        """Определение пользователя в выбранные группы персонала"""

        selected_users = form.cleaned_data.get("users")
        if isinstance(selected_users, QuerySet):
            users_ids = list(selected_users.values_list("id", flat=True))
            if self.view_action == "assign":
                self.group.user_set.add(*users_ids)
            else:
                self.group.user_set.remove(*users_ids)
        return redirect("users:groups")
