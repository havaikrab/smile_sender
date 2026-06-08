from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views
from .apps import UsersConfig
from .forms import CustomUserLoginForm

app_name = UsersConfig.name

urlpatterns: list = [
    path("register/", views.CustomUserRegisterView.as_view(), name="register"),
    path("activate/<int:pk>/<token>/", views.CustomUserActivationView.as_view(), name="activate"),
    path("login/", LoginView.as_view(template_name="users/login.html", form_class=CustomUserLoginForm), name="login"),
    path("logout/", LogoutView.as_view(next_page="distribution:main"), name="logout"),
]
