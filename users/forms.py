from typing import Any

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout, Submit
from django.contrib.auth.forms import UserCreationForm

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
