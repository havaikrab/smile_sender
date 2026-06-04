from django.urls import path

from . import views
from .apps import DistributionConfig

app_name = DistributionConfig.name

urlpatterns = [
    path("", views.HomeView.as_view(), name="main"),
    path("recipients/", views.RecipientListView.as_view(), name="recipients"),
    path("recipients/create_single/", views.SingleRecipientCreateView.as_view(), name="create_single_recipient"),
    path("recipients/update/<int:pk>/", views.RecipientUpdateView.as_view(), name="update_recipient"),
    path("recipients/delete/<int:pk>/", views.RecipientDeleteView.as_view(), name="delete_recipient"),
    path("recipients/download_form/", views.DownloadRecipientsFormView.as_view(), name="download_recipients_form"),
    path("recipients/upload_recipients/", views.UploadRecipientListView.as_view(), name="upload_recipients"),
    path("messages/", views.MessageListView.as_view(), name="messages"),
    path("create_message/", views.MessageCreateView.as_view(), name="create_message"),
    path("message/<int:pk>/", views.MessageDetailView.as_view(), name="message_detail"),
    path("message/update/<int:pk>/", views.MessageUpdateView.as_view(), name="update_message"),
    path("message/delete/<int:pk>/", views.MessageDeleteView.as_view(), name="delete_message"),
    path("mailing_list/", views.MailingListView.as_view(), name="mailing_list"),
    path("create_mailing/", views.MailingCreateView.as_view(), name="create_mailing"),
    path("mailing/<int:pk>/", views.MailingDetailView.as_view(), name="mailing_detail"),
    path("mailing/update/<int:pk>/", views.MailingUpdateView.as_view(), name="update_mailing"),
    path("mailing/delete/<int:pk>/", views.MailingDeleteView.as_view(), name="delete_mailing"),
    path("mailing/start/<int:pk>/", views.MailingStartView.as_view(), name="start_mailing"),
]
