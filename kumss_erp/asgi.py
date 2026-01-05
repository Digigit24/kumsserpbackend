"""
ASGI config for kumss_erp project.

It exposes the ASGI callable as a module-level variable named ``application``.
"""

import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kumss_erp.settings.development')
django.setup()

# Import routing after django.setup()
import apps.communication.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            apps.communication.routing.websocket_urlpatterns
        )
    ),
})
