from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from mailing.tasks import send_mail_task, task_delay_robust


class EmailManager(models.Manager):
    def queue_email(
        self, subject, body, mail_to, html_body, cc=None, bcc=None,
        attachment=None, auto_send=True, email_from=settings.EMAIL_FROM
    ):
        email = self.create(
            subject=subject, body=body, email_from=email_from,
            mail_to=mail_to, html_body=html_body, cc=cc, bcc=bcc, attachment=attachment)
        if auto_send:
            # If this code is running within transaction.atomic block, it should wait for
            # the txn to commit before delaying the task, otherwise inserted email may not be
            # available to the celery worker when it tries to access it.
            task_delay_robust(send_mail_task, email.pk)
        return email


class Email(models.Model):
    subject = models.CharField(max_length=255, verbose_name=_('Subject'))
    mail_to = models.EmailField(verbose_name=_('Mail To'))
    cc = models.TextField(null=True, verbose_name=_('cc'))
    bcc = models.TextField(null=True, verbose_name=_('bcc'))
    email_from = models.EmailField(verbose_name=_('Mail From'))
    body = models.TextField(verbose_name=_('Body'))
    html_body = models.TextField(verbose_name=_('HTML Body'))
    attachment = models.FileField(
        upload_to='invoices/%Y/%m/%d',
        null=True,
        verbose_name=_('Attachment'))
    start_send_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Start Send At'))
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Sent At'))

    objects = EmailManager()
