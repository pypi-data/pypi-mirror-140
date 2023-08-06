import factory.fuzzy
import factory

from mailing.models import Email


class EmailFactory(factory.django.DjangoModelFactory):
    subject = factory.fuzzy.FuzzyText(length=50)
    body = factory.fuzzy.FuzzyText(length=255)
    html_body = factory.fuzzy.FuzzyText(length=255)

    class Meta:
        model = Email
