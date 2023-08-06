from celery import shared_task

import logging

from django.conf import settings
from django.db import transaction

from mailing.services import send_mail

log = logging.getLogger(__name__)


@shared_task
def send_mail_task(email_id):
    """Celery task to send emails."""
    from mailing.models import Email
    task_id = send_mail_task.request.id
    mail = Email.objects.get(pk=email_id)
    try:
        send_mail(mail)
    except Exception:
        log.exception("Failed to send email")
    return {'task_id': task_id}


def task_delay_robust(task, *args):
    """Run celery task keeping db transaction and eager execution in mind."""
    def send_delayed():
        return task.delay(*args)

    delay_on_tx_commit = (
        getattr(settings, 'CELERY_TASK_ALWAYS_EAGER', False) is False and
        transaction.get_connection().in_atomic_block
    )
    if delay_on_tx_commit:
        transaction.on_commit(send_delayed)
    else:
        return send_delayed()
