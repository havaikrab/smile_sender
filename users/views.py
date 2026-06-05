from django.urls import reverse_lazy
from django.views.generic import CreateView


class CustomUserRegisterView(CreateView):
    """Контроллер страницы регистрации нового пользователя"""

    template_name = "users/register.html"
    # form_class =
    success_url = reverse_lazy("distribution:main")
