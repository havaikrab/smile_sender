from typing import Any

from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, TemplateView

from .forms import SingleRecipientForm
from .models import Message, Recipient


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


class MessageCreateView(CreateView):
    """Контроллер создания сообщения рассылки"""

    model = Message
