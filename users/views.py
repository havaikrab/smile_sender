from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CustomUserCreationForm


class CustomUserRegisterView(CreateView):
    """Контроллер страницы регистрации нового пользователя"""

    template_name = "users/register.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("distribution:main")
