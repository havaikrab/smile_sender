from .apps import DistributionConfig
from django.urls import path
from . import views
app_name = DistributionConfig.name

urlpatterns = [
    path('', views.MainView.as_view(), name='main'),
]