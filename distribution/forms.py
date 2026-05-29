from typing import Any

from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Div, Field, Layout, Submit
from django import forms
from django.core.files.base import File
from django.urls import reverse

from .models import Message, Recipient


class SingleRecipientForm(forms.ModelForm):
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


class UploadRecipientListForm(forms.Form):
    """Форма для загрузки excel-файла, содержащего данные получателей"""

    excel_file = forms.FileField(label="Загрузите Excel-файл установленной формы")

    def __init__(self, *args: Any, **kwargs: Any):
        """Стилизация формы"""

        super(UploadRecipientListForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.fields["excel_file"].widget = forms.FileInput(attrs={"accept": ".xlsx"})
        file = Field("excel_file", wrapper_class="sp-bfc")
        submit_button = Submit("submit", "Отправить")
        submit_button.field_classes = "p-2 mt-3 sp-nav-but sp-bfc text-center fs-5"
        self.helper.layout = Layout(file, submit_button)

    def clean_excel_file(self) -> File:
        """Проверка расширения загружаемого файла"""

        file = self.cleaned_data.get("excel_file")
        if isinstance(file, File):
            if isinstance(file.name, str):
                if file.name[-4:] == "xlsx":
                    return file
        raise forms.ValidationError("Загружаемый файл должен иметь расширение xlsx")


class MessageForm(forms.ModelForm):
    """Форма создания нового письма"""

    class Meta:
        """Класс настроек формы"""

        model = Message
        fields = ["title", "content"]

    def __init__(self, *args: Any, **kwargs: Any):
        """Стилизация формы"""

        super(MessageForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        title_field = Field("title", wrapper_class="sp-bfc")
        content_field = Field("content", wrapper_class="sp-bfc")
        submit_button = Submit("submit", "Сохранить")
        submit_button.field_classes = "p-2 mt-3 sp-nav-but sp-bfc text-center fs-5"
        instance = self.instance
        if instance and instance.pk:
            cancel_url = reverse("distribution:message_detail", kwargs={"pk": instance.pk})
        else:
            cancel_url = reverse("distribution:messages")
        cancel_button = HTML(f'<a href="{cancel_url}" class="p-2 mt-3 sp-nav-but sp-bfc text-center fs-5">Отмена</a>')
        buttons_div = Div(submit_button, cancel_button, css_class="d-flex gap-3")
        self.helper.layout = Layout(title_field, content_field, buttons_div)
