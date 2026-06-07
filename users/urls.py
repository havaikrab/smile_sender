from django.urls import path

from . import views
from .apps import UsersConfig

app_name = UsersConfig.name

urlpatterns: list = [path("register/", views.CustomUserRegisterView.as_view(), name="register")]
