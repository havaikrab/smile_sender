from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views
from .apps import UsersConfig
from .forms import CustomUserLoginForm
from .views import (
    CustomUserChangeBlockedStatusView,
    CustomUserDeleteView,
    CustomUserListView,
    CustomUserPasswordChangeView,
    CustomUserPasswordRemakeView,
    CustomUserPasswordResetView,
    CustomUserProfileView,
    CustomUserUpdateView,
    SetCustomUserGroupView,
)

app_name = UsersConfig.name

urlpatterns: list = [
    path("register/", views.CustomUserRegisterView.as_view(), name="register"),
    path("activate/<int:pk>/<token>/", views.CustomUserActivationView.as_view(), name="activate"),
    path("login/", LoginView.as_view(template_name="users/login.html", form_class=CustomUserLoginForm), name="login"),
    path("logout/", LogoutView.as_view(next_page="distribution:main"), name="logout"),
    path("profile/", CustomUserProfileView.as_view(), name="profile"),
    path("update/", CustomUserUpdateView.as_view(), name="update"),
    path("password_change/", CustomUserPasswordChangeView.as_view(), name="password_change"),
    path("delete/", CustomUserDeleteView.as_view(), name="delete"),
    path("password_reset/", CustomUserPasswordResetView.as_view(), name="password_reset"),
    path("password_remake/<uidb64>/<token>/", CustomUserPasswordRemakeView.as_view(), name="password_remake"),
    path("list/", CustomUserListView.as_view(), name="users_list"),
    path(
        "block_switch/<int:pk>/<int:mailing_pk>/",
        CustomUserChangeBlockedStatusView.as_view(),
        name="block_from_mailing",
    ),
    path("block_switch/<int:pk>/", CustomUserChangeBlockedStatusView.as_view(), name="block_from_users_list"),
    path("set_group/<int:pk>/", SetCustomUserGroupView.as_view(), name="set_group"),
]
