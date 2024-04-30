from celery import shared_task
from celery.signals import task_postrun
from bash.consumers import notify_channel_layer
import random
import requests
from celery.utils.log import get_task_logger
from time import sleep
from celery.contrib.abortable import AbortableTask

logger = get_task_logger(__name__)


@shared_task()
def sample_task(url_link):
    from bash.views import map_check

    endpoints, bash_out = map_check(url_link)
    return endpoints, bash_out

@shared_task()
def sample_task_info(url_link):
    from bash.views import info_check

    bash_out = info_check(url_link)
    return bash_out

@shared_task()
def sample_task_configuration(url_link):
    from bash.views import configuration_check

    bash_out = configuration_check(url_link)
    return bash_out

@shared_task()
def sample_task_error(url_link):
    from bash.views import error_check

    bash_out = error_check(url_link)
    return bash_out

@shared_task()
def sample_task_filtering_terms(url_link):
    from bash.views import filtering_terms_check

    bash_out = filtering_terms_check(url_link)
    return bash_out

@shared_task()
def sample_task_endpoints(url_link):
    from bash.views import endpoint_check

    bash_out = endpoint_check(url_link)
    return bash_out

@task_postrun.connect
def task_postrun_handler(task_id, **kwargs):
    """
    When celery task finish, send notification to Django channel_layer, so Django channel would receive
    the event and then send it to web client
    """
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