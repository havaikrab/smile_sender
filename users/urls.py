from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views
from .apps import UsersConfig
from .forms import CustomUserLoginForm
from .views import CustomUserPasswordChangeView, CustomUserProfileView, CustomUserUpdateView

app_name = UsersConfig.name

urlpatterns: list = [
    path("register/", views.CustomUserRegisterView.as_view(), name="register"),
    path("activate/<int:pk>/<token>/", views.CustomUserActivationView.as_view(), name="activate"),
    path("login/", LoginView.as_view(template_name="users/login.html", form_class=CustomUserLoginForm), name="login"),
    path("logout/", LogoutView.as_view(next_page="distribution:main"), name="logout"),
    path("profile/", CustomUserProfileView.as_view(), name="profile"),
    path("update/", CustomUserUpdateView.as_view(), name="update"),
    path("password_change/", CustomUserPasswordChangeView.as_view(), name="password_change"),
]
