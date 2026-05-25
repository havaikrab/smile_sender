import os

from django.http import FileResponse, Http404

from config.settings import BASE_DIR


def get_excel_form() -> FileResponse:
    """Подготавливает к отправке стандартную excel-форму списка получателей"""

    path_to_file = os.path.join(BASE_DIR, "static", "files", "recipients_form.xlsx")
    if not os.path.exists(path_to_file):
        raise Http404
    file = open(path_to_file, "rb")
    response = FileResponse(file, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="recipients_form.xlsx"'
    response["Content-Length"] = os.path.getsize(path_to_file)
    return response
