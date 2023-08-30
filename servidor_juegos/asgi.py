"""
ASGI config for servidor_juegos project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack 
import servidor.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'servidor_juegos.settings')

# Can use http or websocket as protocol
application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            servidor.routing.websocket_urlpatterns
        )
    )
})
