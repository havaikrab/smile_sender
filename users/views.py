from typing import Any

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpRequest
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView

from distribution.services import distribution_logger

from .forms import CustomUserCreationForm
from .models import CustomUser
from .services import send_activate_link


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
