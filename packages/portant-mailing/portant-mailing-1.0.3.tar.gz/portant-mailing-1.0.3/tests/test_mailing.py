import pytest

from django.conf import settings
from django.core import mail
from django.core.management import call_command

from mailing.models import Email
from mailing.services import process_whitelist, send_mail
from mailing.tasks import send_mail_task

from tests.mailing_factories import EmailFactory


@pytest.fixture(autouse=True)
def reset_email_whitelist():
    """Reset email_whitelist setting before and after each test."""
    settings.EMAIL_WHITELIST = []
    yield
    settings.EMAIL_WHITELIST = []


@pytest.mark.django_db
def test_send_email():
    """Test email creation and sending."""
    assert Email.objects.count() == 0
    subject = 'Test'
    mail_to = 'recipient@example.com'
    body = 'Hello'
    email = EmailFactory(
        subject=subject,
        mail_to=mail_to,
        body=body,
    )
    assert Email.objects.count() == 1
    send_mail(email)
    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == 'Test'
    Email.objects.queue_email(subject, body, mail_to, body)
    assert len(mail.outbox) == 2


@pytest.mark.django_db
def test_send_email_when_blocked():
    """Test send_email handles whitelist processing."""
    settings.EMAIL_WHITELIST = ['*@portant.shop']
    mail_to = 'vedran@pinkdroids.com'
    cc = 'vedran@example.com'
    bcc = 'bcc@example.com'
    subject = 'subject'
    email = EmailFactory(
        mail_to=mail_to,
        cc=cc,
        bcc=bcc,
        subject=subject
    )
    email_message = send_mail(email)
    assert email_message.subject == 'Blocked'
    assert email_message.body == 'Blocked'
    assert len(mail.outbox) == 0
    processed = Email.objects.get(pk=email.pk)
    assert processed.subject == '[TEST EMAIL] subject'


@pytest.mark.django_db
def test_send_email_task():
    """Test the shared task function that handles the outgoing emails."""
    email = Email.objects.create(
        subject='Test',
        mail_to='recipient@example.com',
        body='Hello',
    )
    assert Email.objects.count() == 1
    send_mail_task.delay(email.pk)
    assert len(mail.outbox) == 1


@pytest.mark.django_db
def test_sendmail_command():
    """Test the sendmail management command."""
    Email.objects.create(
        subject='Test',
        mail_to='recipient@example.com',
        body='Hello',
    )
    call_command('sendmail')
    assert len(mail.outbox) == 1


@pytest.mark.django_db
def test_whitelist():
    """Test email_whitelist functionality."""
    mail_to = 'vedran@pinkdroids.com'
    cc = 'vedran@example.com'
    bcc = 'bcc@example.com'
    subject = 'subject'
    email = EmailFactory(
        mail_to=mail_to,
        cc=cc,
        bcc=bcc,
        subject=subject
    )

    processed = process_whitelist(email)
    assert len(settings.EMAIL_WHITELIST) == 0
    assert processed.mail_to == mail_to
    assert processed.cc == cc
    assert processed.bcc == bcc
    assert processed.subject == subject
    assert processed.start_send_at is None
    assert processed.sent_at is None

    settings.EMAIL_WHITELIST = ['*@pinkdroids.com']
    email = EmailFactory(
        mail_to=mail_to,
        cc=cc,
        bcc=bcc,
        subject=subject
    )
    processed = process_whitelist(email)
    assert processed.mail_to == mail_to
    assert processed.cc is None
    assert processed.bcc is None
    assert processed.subject == f'[TEST EMAIL] {subject}'
    assert processed.start_send_at is None
    assert processed.sent_at is None

    settings.EMAIL_WHITELIST = ['*@example.com']
    email = EmailFactory(
        mail_to=mail_to,
        cc=cc,
        bcc=bcc,
        subject=subject
    )
    processed = process_whitelist(email)
    assert processed.mail_to == cc
    assert processed.cc == cc
    assert processed.bcc == bcc
    assert processed.subject == f'[TEST EMAIL] {subject}'
    assert processed.start_send_at is None
    assert processed.sent_at is None

    settings.EMAIL_WHITELIST = ['info@pinkdroids.com']
    email = EmailFactory(
        mail_to=mail_to,
        cc=cc,
        bcc=bcc,
        subject=subject
    )
    processed = process_whitelist(email)
    assert processed.mail_to == 'vedranATpinkdroids.com'
    assert processed.cc == 'vedranATexample.com'
    assert processed.bcc == 'bccATexample.com'
    assert processed.subject == f'[TEST EMAIL] {subject}'
    assert processed.start_send_at is not None
    assert processed.sent_at is not None

    settings.EMAIL_WHITELIST = [mail_to]
    email = EmailFactory(
        mail_to=mail_to,
        cc=cc,
        bcc=bcc,
        subject=subject
    )
    processed = process_whitelist(email)
    assert processed.mail_to == mail_to
    assert processed.cc is None
    assert processed.bcc is None
    assert processed.subject == f'[TEST EMAIL] {subject}'
    assert processed.start_send_at is None
    assert processed.sent_at is None

    settings.EMAIL_WHITELIST = ['*@example.com']
    email = EmailFactory(
        mail_to=mail_to,
        cc=None,
        bcc=None,
        subject=subject
    )
    processed = process_whitelist(email)
    assert processed.mail_to == 'vedranATpinkdroids.com'
    assert processed.cc is None
    assert processed.bcc is None
    assert processed.subject == f'[TEST EMAIL] {subject}'
    assert processed.start_send_at is not None
    assert processed.sent_at is not None
