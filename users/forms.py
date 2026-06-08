from typing import Any

from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Div, Field, Layout, Submit
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm, UserCreationForm
from django.urls import reverse

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """Форма регистрации нового пользователя"""

    class Meta(UserCreationForm.Meta):
        """Класс настроек формы"""

        model = CustomUser
        fields = ("first_name", "last_name", "phone", "company", "username", "email", "password1", "password2")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Стилизация формы"""

        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        first_name = Field("first_name", wrapper_class="mt-2")
        others_fields = [Field(field, wrapper_class="my-5") for field in CustomUserCreationForm.Meta.fields[1:]]
        submit_button = Submit("submit", "Зарегистрироваться")
        submit_button.field_classes = "p-2 mt-5 sp-nav-but sp-bfc text-center fs-5"
        self.helper.layout = Layout(first_name, *others_fields, submit_button)


class CustomUserLoginForm(AuthenticationForm):
    """Форма авторизации пользователя"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Стилизация формы"""

        super(CustomUserLoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        submit_button = Submit("submit", "Войти")
        submit_button.field_classes = "p-2 mt-3 sp-nav-but sp-bfc text-center fs-5"
        restore_password_url = reverse("distribution:main")
        restore_button = HTML(f"""<a href="{restore_password_url}"class="p-2 mt-3 sp-nav-but sp-bfc text-center fs-5">
            Восстановить пароль</a>""")
        buttons_div = Div(submit_button, restore_button, css_class="d-flex gap-3")
        self.helper.layout = Layout("username", "password", buttons_div)


class CustomUserUpdateForm(UserChangeForm):
    """Форма для редактирования личных данных пользователя"""

    class Meta(UserChangeForm.Meta):
        """Класс настроек формы"""

        model = CustomUser
        fields = ("last_name", "first_name", "email", "username", "company", "phone")  # type: ignore

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Стилизация формы"""

        super(CustomUserUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        last_name = Field("last_name", wrapper_class="mt-2")
        others_fields = [Field(field, wrapper_class="my-5") for field in CustomUserUpdateForm.Meta.fields[1:]]
        submit_button = Submit("submit", "Сохранить")
        submit_button.field_classes = "p-2 mt-5 sp-nav-but sp-bfc text-center fs-5"
        cancel_url = reverse("users:profile")
        cancel_button = HTML(f'<a href="{cancel_url}"class="p-2 mt-5 sp-nav-but sp-bfc text-center fs-5">Отмена</a>')
        buttons_div = Div(submit_button, cancel_button, css_class="d-flex gap-3")
        self.helper.layout = Layout(last_name, *others_fields, buttons_div)
