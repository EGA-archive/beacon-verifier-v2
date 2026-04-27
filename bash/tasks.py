from celery import shared_task
from celery.signals import task_postrun
from bash.consumers import notify_channel_layer
import random
import requests
from celery.utils.log import get_task_logger
from time import sleep
from celery.contrib.abortable import AbortableTask
from celery.result import AsyncResult

logger = get_task_logger(__name__)

@shared_task(bind=True, base=AbortableTask)
def verification(self, url_link, function_name):
    from bash.views import info_check, endpoint_check, filtering_terms_check, error_check, configuration_check, map_check

    functions = {
        "info_check": info_check,
        "endpoint_check": endpoint_check,
        "filtering_terms_check": filtering_terms_check,
        "error_check": error_check,
        "configuration_check": configuration_check,
        "map_check": map_check
    }

    if self.is_aborted():
        return 'Task stopped!'
    function = functions[function_name]
    bash_out = function(url_link)
    return bash_out 

@task_postrun.connect
def task_postrun_handler(task_id, **kwargs):
    notify_channel_layer(task_id)

@shared_task(bind=True)
def task_retry(self):
    try:
        raise Exception()

        #requests.post('https://...')
    except Exception as e:
        logger.error('retry after 10 secs cause of exception')
        raise self.retry(exc=e, countdown=10)

@shared_task(bind=True, base=AbortableTask)
def count(self):
    for i in range(10):
        if self.is_aborted():
            return 'Task stopped!'
        print(i)
        sleep(1)
    return 'DONE!' 

@shared_task(bind=True, base=AbortableTask)
def cancel(task_id):
    task = count.AsyncResult(task_id)
    task.abort()
    return 'Canceled!'