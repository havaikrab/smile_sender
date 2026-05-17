from django.views.generic import TemplateView

class MainView(TemplateView):
    template_name = 'distribution/main_page.html'
