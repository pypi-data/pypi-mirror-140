from mailing.celery import app


app.conf.update(CELERY_ALWAYS_EAGER=True)

INSTALLED_APPS = [
    'mailing',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'mailing',
    }
}

EMAIL_FROM = 'mailing@example.com'
