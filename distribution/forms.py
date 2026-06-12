import datetime
from typing import Any, cast

from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Div, Field, Layout, Submit
from django import forms
from django.core.exceptions import ValidationError
from django.core.files.base import File
from django.urls import reverse
from django.utils import timezone

from .models import Mailing, Message, Recipient


class SingleRecipientForm(forms.ModelForm):
    """Форма для создания одного получателя рассылок"""

    class Meta:
        """Класс настроек формы"""

        model = Recipient
        fields = ("email", "first_name", "middle_name", "last_name", "comment")

    def __init__(self, *args: Any, **kwargs: Any):
        """Стилизация формы"""

        super(SingleRecipientForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        email_field = Field("email", wrapper_class="mb-5 mt-2")
        others_fields = [Field(field, wrapper_class="my-5") for field in SingleRecipientForm.Meta.fields[1:]]
        submit_button = Submit("submit", "Сохранить")
        submit_button.field_classes = "p-2 mt-5 sp-nav-but sp-bfc text-center fs-5"
        self.helper.layout = Layout(email_field, *others_fields, submit_button)


class UploadRecipientListForm(forms.Form):
    """Форма для загрузки excel-файла, содержащего данные получателей"""

    excel_file = forms.FileField(label="Загрузите Excel-файл установленной формы")

    def __init__(self, *args: Any, **kwargs: Any):
        """Стилизация формы"""

        super(UploadRecipientListForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.fields["excel_file"].widget = forms.FileInput(attrs={"accept": ".xlsx"})
        submit_button = Submit("submit", "Отправить")
        submit_button.field_classes = "p-2 mt-5 sp-nav-but sp-bfc text-center fs-5"
        self.helper.layout = Layout("excel_file", submit_button)

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
        fields = ("title", "content")

    def __init__(self, *args: Any, **kwargs: Any):
        """Стилизация формы"""

        super(MessageForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        title_field = Field("title", wrapper_class="mt-2")
        content_field = Field("content", wrapper_class="my-5")
        submit_button = Submit("submit", "Сохранить")
        submit_button.field_classes = "p-2 mt-5 sp-nav-but sp-bfc text-center fs-5"
        instance = self.instance
        if instance and instance.pk:
            cancel_url = reverse("distribution:message_detail", kwargs={"pk": instance.pk})
        else:
            cancel_url = reverse("distribution:messages")
        cancel_button = HTML(f'<a href="{cancel_url}" class="p-2 mt-5 sp-nav-but sp-bfc text-center fs-5">Отмена</a>')
        buttons_div = Div(submit_button, cancel_button, css_class="d-flex gap-3")
        self.helper.layout = Layout(title_field, content_field, buttons_div)


class MailingForm(forms.ModelForm):
    """Форма создания новой рассылки"""

    class Meta:
        """Класс настроек формы"""

        model = Mailing
        fields = ("start_time", "end_time", "message", "recipients")
        widgets = {
            "start_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "recipients": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args: Any, **kwargs: Any):
        """Стилизация формы"""

        user_messages = kwargs.pop("user_messages")
        super(MailingForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        instance = self.instance
        if instance.pk:
            default_start = timezone.localtime(instance.start_time)
            default_end = timezone.localtime(instance.end_time)
        else:
            default_start = timezone.localtime() + datetime.timedelta(hours=1)
            default_end = timezone.localtime() + datetime.timedelta(hours=2)
        self.initial["start_time"] = datetime.datetime.strftime(default_start, "%Y-%m-%dT%H:%M")
        self.initial["end_time"] = datetime.datetime.strftime(default_end, "%Y-%m-%dT%H:%M")
        start_time = Field("start_time", wrapper_class="mb-5 mt-2", css_class="sp-bfc")
        end_time = Field("end_time", wrapper_class="my-5", css_class="sp-bfc")
        self.fields["message"] = cast(forms.ModelChoiceField, self.fields["message"])
        self.fields["message"].queryset = user_messages  # type: ignore
        message_field = Field("message", wrapper_class="my-5")
        recipients = Field("recipients", wrapper_class="my-5", css_class="sp-check-scroll")
        submit_button = Submit("submit", "Сохранить")
        submit_button.field_classes = "p-2 mt-5 sp-nav-but sp-bfc text-center fs-5"
        if instance and instance.pk:
            cancel_url = reverse("distribution:mailing_detail", kwargs={"pk": instance.pk})
        else:
            cancel_url = reverse("distribution:mailing_list")
        cancel_button = HTML(f'<a href="{cancel_url}" class="p-2 mt-5 sp-nav-but sp-bfc text-center fs-5">Отмена</a>')
        buttons_div = Div(submit_button, cancel_button, css_class="d-flex gap-3")
        self.helper.layout = Layout(start_time, end_time, message_field, recipients, buttons_div)

    def clean_start_time(self) -> datetime.datetime:
        """Ограничение: начало рассылки не может быть установлено в прошлом"""

        instance = self.instance
        time_now = timezone.localtime()
        start_time = self.cleaned_data.get("start_time")
        if isinstance(start_time, datetime.datetime):
            if instance.pk:
                initial_start = instance.start_time
                if start_time == initial_start:
                    return start_time
            if start_time > time_now:
                return start_time
        raise ValidationError("Нельзя установить старт рассылки в прошлом.")

    def clean_end_time(self) -> datetime.datetime:
        """Ограничение: время завершения рассылки не может быть установлено раньше времени ее начала"""

        start_time = self.cleaned_data.get("start_time")
        end_time = self.cleaned_data.get("end_time")
        time_now = timezone.localtime()
        if isinstance(start_time, datetime.datetime) and isinstance(end_time, datetime.datetime):
            if end_time > start_time and end_time > time_now:
                return end_time
        raise ValidationError("Значение не может быть установлено в прошлом или раньше времени начала рассылки.")
