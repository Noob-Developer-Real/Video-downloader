'''
celery is used for the tasks which will be going to be distributed
this portion going to be doing mainly the hard tasks only 

'''
from celery import Celery
from celery.schedules import crontab
import os

#<--- Celery configurations --->
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks() 

#<--- For the removal of downloaded file --->
app.conf.beat_schedule = {
    'cleanup-every-5-minutes': {
        'task': 'core.tasks.cleanup_expired_files',
        'schedule': crontab(minute='*/5'),
        'args': (10,)  # TTL = 10 minutes
    },
}