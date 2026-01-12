"""
ASGI config for kumss_erp project.

It exposes the ASGI callable as a module-level variable named ``application``.

Supports both HTTP and WebSocket protocols with Django Channels.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kumss_erp.settings.development')
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
import apps.communication.routing
from apps.communication.middleware import TokenAuthMiddleware

# ASGI application with WebSocket support
application = ProtocolTypeRouter({
    # HTTP requests
    "http": get_asgi_application(),

    # WebSocket connections
    "websocket": AllowedHostsOriginValidator(
        TokenAuthMiddleware(
            URLRouter(
                apps.communication.routing.websocket_urlpatterns
            )
        )
    ),
})
