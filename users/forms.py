from typing import Any, Optional

from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Div, Field, Layout, Submit
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
    UserChangeForm,
    UserCreationForm,
)
from django.contrib.auth.models import Group
from django.core.mail import send_mail as base_send_mail
from django.forms import CheckboxSelectMultiple, Form, ModelForm, ModelMultipleChoiceField, PasswordInput
from django.urls import reverse

from config.settings import EMAIL_HOST_USER, SITE_URL

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
        restore_password_url = reverse("users:password_reset")
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


class CustomUserPasswordChangeForm(PasswordChangeForm):
    """Форма для смены пароля от аккаунта"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Стилизация формы"""

        super(CustomUserPasswordChangeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        submit_button = Submit("submit", "Подтвердить")
        submit_button.field_classes = "p-2 mt-5 sp-nav-but sp-bfc text-center fs-5"
        cancel_url = reverse("users:profile")
        cancel_button = HTML(f'<a href="{cancel_url}" class="p-2 mt-5 sp-nav-but sp-bfc text-center fs-5">Отмена</a>')
        buttons_div = Div(submit_button, cancel_button, css_class="d-flex gap-3")
        self.helper.layout = Layout("old_password", "new_password1", "new_password2", buttons_div)


class CustomUserDeleteForm(ModelForm):
    """Форма для подтверждения удаления аккаунта"""

    class Meta:
        """Класс настроек формы"""

        model = CustomUser
        fields = ["password"]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Стилизация формы"""

        super(CustomUserDeleteForm, self).__init__(*args, **kwargs)
        self.fields["password"].widget = PasswordInput()
        self.helper = FormHelper()
        self.helper.form_tag = False
        submit_button = Submit("submit", "Удалить")
        submit_button.field_classes = "p-2 mt-5 sp-dngr-but sp-bfc text-center fs-5"
        cancel_url = reverse("users:profile")
        cancel_button = HTML(f'<a href="{cancel_url}" class="p-2 mt-5 sp-nav-but sp-bfc text-center fs-5">Отмена</a>')
        buttons_div = Div(submit_button, cancel_button, css_class="d-flex gap-3")
        self.helper.layout = Layout("password", buttons_div)


class CustomUserPasswordResetForm(PasswordResetForm):
    """Форма для сброса пароля от аккаунта для его дальнейшего восстановления"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Стилизация формы"""

        super(CustomUserPasswordResetForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        submit_button = Submit("submit", "Подтвердить")
        submit_button.field_classes = "p-2 mt-3 sp-nav-but sp-bfc text-center fs-5"
        cancel_url = reverse("distribution:main")
        cancel_button = HTML(f'<a href="{cancel_url}"class="p-2 mt-3 sp-nav-but sp-bfc text-center fs-5">Отмена</a>')
        buttons_div = Div(submit_button, cancel_button, css_class="d-flex gap-3")
        self.helper.layout = Layout("email", buttons_div)

    def send_mail(
        self,
        subject_template_name: str | None,
        email_template_name: str | None,
        context: dict,
        from_email: Optional[str],
        to_email: str,
        html_email_template_name: str | None = None,
    ) -> None:
        """Переопределение содержимого письма со ссылкой для восстановления пароля"""

        reset_link = (
            SITE_URL
            + "/"
            + reverse("users:password_remake", kwargs={"uidb64": context["uid"], "token": context["token"]})
        )
        message = f"Перейдите по данной ссылке и укажите новый пароль от аккаунта Smile Sender:\n {reset_link}"
        base_send_mail(
            "Восстановление пароля Smile Sender", message, from_email=EMAIL_HOST_USER, recipient_list=[to_email]
        )


class CustomUserPasswordSetForm(SetPasswordForm):
    """Форма для установки нового пароля от аккаунта"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Стилизация формы"""

        super(CustomUserPasswordSetForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        submit_button = Submit("submit", "Сохранить")
        submit_button.field_classes = "p-2 mt-5 sp-nav-but sp-bfc text-center fs-5"
        cancel_url = reverse("distribution:main")
        cancel_button = HTML(f'<a href="{cancel_url}" class="p-2 mt-5 sp-nav-but sp-bfc text-center fs-5">Отмена</a>')
        buttons_div = Div(submit_button, cancel_button, css_class="d-flex gap-3")
        self.helper.layout = Layout("new_password1", "new_password2", buttons_div)


class SetCustomUserGroupForm(Form):
    """Форма для добавления пользователя в определенную группу персонала"""

    groups = ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=CheckboxSelectMultiple(attrs={"size": "3"}),
        required=True,
        label="Группы персонала",
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Стилизация формы"""

        super(SetCustomUserGroupForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        groups = Field("groups", css_class="sp-check-scroll")
        submit_button = Submit("submit", "Назначить")
        submit_button.field_classes = "p-2 sp-nav-but sp-bfc text-center fs-5"
        cancel_url = reverse("users:users_list")
        cancel_button = HTML(f'<a href="{cancel_url}" class="p-2 sp-nav-but sp-bfc text-center fs-5">Отмена</a>')
        buttons_div = Div(submit_button, cancel_button, css_class="d-flex gap-3 mt-5")
        self.helper.layout = Layout(groups, buttons_div)


class AssignGroupForm(Form):
    """Форма выбора пользователей для добавления в группу"""

    users = ModelMultipleChoiceField(
        queryset=CustomUser.objects.none(),
        widget=CheckboxSelectMultiple(attrs={"size": "10"}),
        required=True,
        label="Пользователи",
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Стилизация формы"""

        users_list = kwargs.pop("users_list")
        view_action = kwargs.pop("view_action")
        super(AssignGroupForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.fields["users"].queryset = users_list  # type: ignore
        users_field = Field("users", css_class="sp-check-scroll")
        if view_action == "assign":
            submit_button = Submit("submit", "Назначить")
        else:
            submit_button = Submit("submit", "Исключить")
        submit_button.field_classes = "p-2 sp-nav-but sp-bfc text-center fs-5"
        cancel_url = reverse("users:groups")
        cancel_button = HTML(f'<a href="{cancel_url}" class="p-2 sp-nav-but sp-bfc text-center fs-5">Отмена</a>')
        buttons_div = Div(submit_button, cancel_button, css_class="d-flex gap-3 mt-5")
        self.helper.layout = Layout(users_field, buttons_div)
