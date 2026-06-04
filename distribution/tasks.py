from celery import shared_task

from distribution.services import execute_mailing


@shared_task
def shared_send_mailing_task(mailing_id: int) -> None:
    """Асинхронное осуществление рассылки"""

    execute_mailing(mailing_id)
