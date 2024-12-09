import os

from celery import Celery
from django.conf import settings
from django.utils.timezone import timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.backend.settings")

app = Celery("backend")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.broker_url = settings.CELERY_BROKER_URL

app.conf.update(
    CELERY_BROKER_URL=settings.CELERY_BROKER_URL,
    CELERY_BEAT_SCHEDULE={
        "quiz_notification": {
            "task": "backend.apps.quiz.tasks.notify_users",
            "schedule": timedelta(days=1),
        },
    },
)

app.autodiscover_tasks()
