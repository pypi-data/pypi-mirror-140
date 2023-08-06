from django.core.management.base import BaseCommand

from mailing.models import Email
from mailing.services import send_mail


class Command(BaseCommand):
    help = 'Sends mail if start_send_at is null'

    def handle(self, *args, **options):
        mails = Email.objects.filter(start_send_at__isnull=True)
        for mail in mails:
            send_mail(mail)
