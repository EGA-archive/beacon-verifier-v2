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
def sample_task(self, url_link):
    from bash.views import map_check
    if self.is_aborted():
        return 'Task stopped!'

    endpoints, bash_out = map_check(url_link)
    return endpoints, bash_out

@shared_task(bind=True, base=AbortableTask)
def sample_task_info(self, url_link):
    from bash.views import info_check
    if self.is_aborted():
        return 'Task stopped!'

    bash_out = info_check(url_link)
    return bash_out

@shared_task(bind=True, base=AbortableTask)
def sample_task_configuration(self, url_link):
    from bash.views import configuration_check
    if self.is_aborted():
        return 'Task stopped!'
    bash_out = configuration_check(url_link)
    return bash_out

@shared_task(bind=True, base=AbortableTask)
def sample_task_error(self, url_link):
    from bash.views import error_check
    if self.is_aborted():
        return 'Task stopped!'
    bash_out = error_check(url_link)
    return bash_out

@shared_task(bind=True, base=AbortableTask)
def sample_task_filtering_terms(self, url_link):
    from bash.views import filtering_terms_check
    if self.is_aborted():
        return 'Task stopped!'
    bash_out = filtering_terms_check(url_link)
    return bash_out

@shared_task(bind=True, base=AbortableTask)
def sample_task_endpoints(self, url_link):
    if '}/g_variants' in url_link:
        return [url_link, []]
    from bash.views import endpoint_check
    if self.is_aborted():
        return 'Task stopped!'
    bash_out = endpoint_check(url_link)
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