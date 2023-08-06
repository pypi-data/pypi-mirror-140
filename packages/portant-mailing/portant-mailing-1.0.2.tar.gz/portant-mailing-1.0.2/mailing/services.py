import os
from typing import List, Union

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone as tz


def send_mail(email) -> EmailMultiAlternatives:
    """Send an email message."""
    email = process_whitelist(email)
    if email.sent_at is not None:
        return EmailMultiAlternatives('Blocked', 'Blocked')

    email.start_send_at = tz.now()
    email.save()

    email_message = EmailMultiAlternatives(
        email.subject, email.body, email.email_from, [email.mail_to])
    email_message.attach_alternative(email.html_body, "text/html")
    if email.cc:
        email_message.cc = email.cc.split()
    if email.bcc:
        email_message.bcc = email.bcc.split()
    if email.attachment:
        name = os.path.basename(email.attachment.url)
        email_message.attach(name, email.attachment.read())

    email_message.send()

    email.sent_at = tz.now()
    email.save()

    return email_message


def _is_email_whitelisted(addr: Union[str, None]) -> bool:
    """
    Check if email is contained within an EMAIL_WHITELIST setting.

    It will attempt to match an exact address or same domain match
    if the whitelisted address is listed as `*@domain.com`.
    """
    whitelist: List[str] = settings.EMAIL_WHITELIST
    if not addr:
        return False
    elif addr in whitelist:
        return True

    whitelisted_by_domain = False
    for e in whitelist:
        if not e.startswith('*'):
            continue
        _, whitelisted_domain = e.split('@')
        _, domain = addr.split('@')
        if domain == whitelisted_domain:
            whitelisted_by_domain = True
            break

    return whitelisted_by_domain


def process_whitelist(email):
    """
    Compare all recipients against the EMAIL_WHITELIST setting and alter instance if needed.

    Checks for each of mail_to, cc and bcc addresses
    - If the whitelist is empty or each recipient is whitelisted does not change any email
    - If the whitelist is not empty, appends [TEST EMAIL] to subject
    - If no recipient is valid, replaces `@` with `AT` for each recipient
        and marks the Email as sent.
    - If any recipient is valid, sends to all valid recipients.
    - If `mail_to` is not valid, sets a valid `cc` or `bcc` as `mail_to` .
    """
    whitelist_empty = len(settings.EMAIL_WHITELIST) == 0
    if email.sent_at or whitelist_empty:
        return email

    # Add TEST EMAIL prefix if sent from an environment that restricts recipients
    if not whitelist_empty:
        email.subject = f'[TEST EMAIL] {email.subject}'

    to_whitelisted = _is_email_whitelisted(email.mail_to)
    cc_whitelisted = _is_email_whitelisted(email.cc)
    bcc_whitelisted = _is_email_whitelisted(email.bcc)

    if not (to_whitelisted or cc_whitelisted or bcc_whitelisted):
        email.mail_to = email.mail_to.replace('@', 'AT')
        email.cc = email.cc and email.cc.replace('@', 'AT')
        email.bcc = email.bcc and email.bcc.replace('@', 'AT')
        email.start_send_at = tz.now()
        email.sent_at = tz.now()
        email.save()
        return email

    if not cc_whitelisted:
        email.cc = None
    if not bcc_whitelisted:
        email.bcc = None
    # to_email can't be null, so set it to any of the whitelisted
    if not to_whitelisted:
        email.mail_to = email.cc or email.bcc

    email.save()
    return email
