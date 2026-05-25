from typing import Any

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout, Submit
from django.forms import ModelForm

from .models import Recipient


class SingleRecipientForm(ModelForm):
    """Форма для создания одного получателя рассылок"""

    class Meta:
        """Класс настроек формы"""

        model = Recipient
        fields = ["email", "first_name", "middle_name", "last_name", "comment"]

    def __init__(self, *args: Any, **kwargs: Any):
        """Стилизация формы"""

        super(SingleRecipientForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        email_field = Field("email", wrapper_class="sp-bfc")
        first_name = Field("first_name", wrapper_class="sp-bfc")
        middle_name = Field("middle_name", wrapper_class="sp-bfc")
        last_name = Field("last_name", wrapper_class="sp-bfc")
        comment_field = Field("comment", wrapper_class="sp-bfc")
        submit_button = Submit("submit", "Сохранить")
        submit_button.field_classes = "p-2 sp-nav-but sp-bfc text-center fs-5"
        self.helper.layout = Layout(email_field, first_name, middle_name, last_name, comment_field, submit_button)
