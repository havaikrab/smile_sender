from django.views.generic import CreateView, TemplateView

from .models import Message


class HomeView(TemplateView):
    """Контроллер главной страницы приложения distribution"""

    template_name = "distribution/home_page.html"


class MessageCreateView(CreateView):
    """Контроллер создания сообщения рассылки"""

    model = Message
