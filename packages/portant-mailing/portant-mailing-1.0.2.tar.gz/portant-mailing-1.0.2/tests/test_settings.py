from celery import Celery

INSTALLED_APPS = [
    'mailing',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'mailing',
    }
}

MAILING_EMAIL_FROM = 'mailing@example.com'

CELERY_TASK_ALWAYS_EAGER = True

app = Celery('mailing')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

print(app.conf.__dict__.keys())
