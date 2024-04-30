import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from bash import routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'verifierweb.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    'websocket': URLRouter(
        routing.urlpatterns
    )
})