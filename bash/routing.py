from django.urls import path

from bash import consumers


urlpatterns = [
    path('ws/task_status/<task_id>/', consumers.TaskStatusConsumer.as_asgi()),
]