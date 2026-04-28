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
def verification(self, url_link, include, granularity, test_mode, function_name):
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
    bash_out = function(url_link, include, granularity, test_mode)
    return bash_out 