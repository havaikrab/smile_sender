from celery import shared_task

from distribution.models import Mailing
from distribution.services import send_mails


@shared_task
def shared_send_mailing_task(mailing_id: int) -> None:
    """Асинхронное осуществление рассылки"""

    mailing = Mailing.objects.get(pk=mailing_id)
    send_mails(mailing)
