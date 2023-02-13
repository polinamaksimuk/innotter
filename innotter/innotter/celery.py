import os

from celery import Celery

from innotter import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "innotter.settings")
app = Celery("innotter", broker=settings.CELERY_BROKER_URL)

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
