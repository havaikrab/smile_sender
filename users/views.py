from django.contrib import messages
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CustomUserCreationForm
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
        return redirect(self.success_url)
