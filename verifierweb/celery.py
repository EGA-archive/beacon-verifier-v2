import os

from celery import Celery

from django.conf import settings

# this code copied from manage.py
# set the default Django settings module for the 'celery' app.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'verifierweb.settings')

# you can change the name here
app = Celery("verifierweb")

# read config from Django settings, the CELERY namespace would make celery
# config keys has `CELERY` prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# discover and load tasks.py from from all registered Django apps
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task
def divide(x, y):
    #from celery.contrib import rdb
    #rdb.set_trace()

    # this is for test purposes
    import time
    time.sleep(10)
    return x / y