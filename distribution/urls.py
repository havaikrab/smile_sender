from django.urls import path

from . import views
from .apps import DistributionConfig

app_name = DistributionConfig.name

urlpatterns = [
    path("", views.HomeView.as_view(), name="main"),
    path("recipients/", views.RecipientListView.as_view(), name="recipients"),
    path("recipients/create_single/", views.SingleRecipientCreateView.as_view(), name="create_single_recipient"),
    path("recipients/download_form/", views.DownloadRecipientsFormView.as_view(), name="download_recipients_form"),
    path("recipients/upload_recipients/", views.UploadRecipientListView.as_view(), name="upload_recipients"),
]
