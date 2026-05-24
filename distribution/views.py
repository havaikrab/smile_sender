from django.views.generic import CreateView, ListView, TemplateView

from .models import Message, Recipient


class HomeView(TemplateView):
    """Контроллер главной страницы приложения distribution"""

    template_name = "distribution/home_page.html"


class RecipientListView(ListView):
    """Контроллер страницы списка получателей"""

    model = Recipient


class MessageCreateView(CreateView):
    """Контроллер создания сообщения рассылки"""

    model = Message
