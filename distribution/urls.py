from django.urls import path

from . import views
from .apps import DistributionConfig

app_name = DistributionConfig.name

urlpatterns = [
    path("", views.HomeView.as_view(), name="main"),
    path("recipients/", views.RecipientListView.as_view(), name="recipients"),
]
