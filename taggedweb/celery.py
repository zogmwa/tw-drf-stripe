import os

from celery import Celery
from celery.schedules import crontab
import taggedweb.tasks

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taggedweb.settings')

app = Celery('taggedweb')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# https://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html#crontab-schedules
app.conf.beat_schedule = {
    'send-report-every-single-minute': {
        'task': 'taggedweb.tasks.update_sitemap',
        'schedule': crontab(),  # change to `crontab(minute=0, hour=0)` if you want it to run daily at midnight
    },
}
