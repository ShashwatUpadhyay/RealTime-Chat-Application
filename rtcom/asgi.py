"""
ASGI config for rtcom project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rtcom.settings')

# application = get_asgi_application()
from base import consumers
from django.urls import path
from channels.routing import ProtocolTypeRouter,URLRouter

ws_patterns = [
    path("ws/chat/<code>", consumers.ChatConsumer),
]

application = ProtocolTypeRouter({
    "websocket":(
        (
            URLRouter(
                ws_patterns
            )
        )
    ),
})
